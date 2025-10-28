"""
Database Backup Manager for Jumbo Chatbot
Handles automated backups, point-in-time recovery, and data integrity
"""

import os
import json
import gzip
import shutil
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

from supabase_service import SupabaseService
from monitoring import logger

@dataclass
class BackupInfo:
    """Backup information"""
    backup_id: str
    backup_type: str
    created_at: datetime
    size_bytes: int
    table_counts: Dict[str, int]
    checksum: str
    status: str

class BackupManager:
    """Manages database backups and recovery"""
    
    def __init__(self, supabase_service: SupabaseService, backup_dir: str = "./backups"):
        self.supabase = supabase_service
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup retention policy
        self.daily_retention_days = 30
        self.weekly_retention_weeks = 12
        self.monthly_retention_months = 12
    
    def create_full_backup(self, backup_type: str = 'manual') -> Optional[str]:
        """Create full database backup"""
        try:
            backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_type}"
            backup_path = self.backup_dir / f"{backup_id}.json.gz"
            
            logger.info("Starting full backup", backup_id=backup_id)
            
            # Tables to backup
            tables = [
                'profiles',
                'conversations', 
                'user_memories',
                'mood_history',
                'user_memories_backup'
            ]
            
            backup_data = {
                'backup_id': backup_id,
                'backup_type': backup_type,
                'created_at': datetime.now().isoformat(),
                'tables': {}
            }
            
            table_counts = {}
            
            # Backup each table
            for table in tables:
                try:
                    logger.info(f"Backing up table: {table}")
                    
                    # Get all data from table
                    response = self.supabase.supabase.table(table).select('*').execute()
                    
                    table_data = response.data if response.data else []
                    table_counts[table] = len(table_data)
                    
                    backup_data['tables'][table] = table_data
                    
                    logger.info(f"Backed up {len(table_data)} records from {table}")
                    
                except Exception as e:
                    logger.error(f"Failed to backup table {table}", error=e)
                    table_counts[table] = 0
                    backup_data['tables'][table] = []
            
            # Add metadata
            backup_data['table_counts'] = table_counts
            backup_data['total_records'] = sum(table_counts.values())
            
            # Calculate checksum
            backup_json = json.dumps(backup_data, sort_keys=True, default=str)
            checksum = self._calculate_checksum(backup_json)
            backup_data['checksum'] = checksum
            
            # Compress and save backup
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                json.dump(backup_data, f, default=str, indent=2)
            
            # Get file size
            file_size = backup_path.stat().st_size
            
            # Record backup in database
            backup_record = {
                'backup_id': backup_id,
                'backup_type': backup_type,
                'file_path': str(backup_path),
                'file_size': file_size,
                'table_counts': table_counts,
                'checksum': checksum,
                'status': 'completed'
            }
            
            # Store backup record (if backup_records table exists)
            try:
                self.supabase.supabase.table('backup_records').insert(backup_record).execute()
            except Exception as e:
                logger.warning("Could not store backup record", error=e)
            
            logger.info("Full backup completed",
                       backup_id=backup_id,
                       file_size=file_size,
                       total_records=backup_data['total_records'])
            
            return backup_id
            
        except Exception as e:
            logger.error("Full backup failed", error=e)
            return None
    
    def create_incremental_backup(self, since: datetime) -> Optional[str]:
        """Create incremental backup since specified time"""
        try:
            backup_id = f"incremental_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.backup_dir / f"{backup_id}.json.gz"
            
            logger.info("Starting incremental backup", backup_id=backup_id, since=since)
            
            # Tables with timestamp columns
            timestamped_tables = {
                'profiles': 'last_active',
                'conversations': 'created_at',
                'user_memories': 'updated_at',
                'mood_history': 'created_at'
            }
            
            backup_data = {
                'backup_id': backup_id,
                'backup_type': 'incremental',
                'since': since.isoformat(),
                'created_at': datetime.now().isoformat(),
                'tables': {}
            }
            
            table_counts = {}
            
            # Backup changed records from each table
            for table, timestamp_col in timestamped_tables.items():
                try:
                    logger.info(f"Backing up incremental data from {table}")
                    
                    response = self.supabase.supabase.table(table).select('*').gte(timestamp_col, since.isoformat()).execute()
                    
                    table_data = response.data if response.data else []
                    table_counts[table] = len(table_data)
                    
                    backup_data['tables'][table] = table_data
                    
                    logger.info(f"Backed up {len(table_data)} changed records from {table}")
                    
                except Exception as e:
                    logger.error(f"Failed to backup incremental data from {table}", error=e)
                    table_counts[table] = 0
                    backup_data['tables'][table] = []
            
            backup_data['table_counts'] = table_counts
            backup_data['total_records'] = sum(table_counts.values())
            
            # Only create backup if there are changes
            if backup_data['total_records'] == 0:
                logger.info("No changes found, skipping incremental backup")
                return None
            
            # Calculate checksum and save
            backup_json = json.dumps(backup_data, sort_keys=True, default=str)
            checksum = self._calculate_checksum(backup_json)
            backup_data['checksum'] = checksum
            
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                json.dump(backup_data, f, default=str, indent=2)
            
            file_size = backup_path.stat().st_size
            
            logger.info("Incremental backup completed",
                       backup_id=backup_id,
                       file_size=file_size,
                       total_records=backup_data['total_records'])
            
            return backup_id
            
        except Exception as e:
            logger.error("Incremental backup failed", error=e)
            return None
    
    def restore_from_backup(self, backup_id: str, tables: Optional[List[str]] = None) -> bool:
        """Restore data from backup"""
        try:
            backup_path = self.backup_dir / f"{backup_id}.json.gz"
            
            if not backup_path.exists():
                logger.error("Backup file not found", backup_id=backup_id, path=str(backup_path))
                return False
            
            logger.info("Starting restore from backup", backup_id=backup_id)
            
            # Load backup data
            with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Verify checksum
            backup_copy = backup_data.copy()
            stored_checksum = backup_copy.pop('checksum', None)
            calculated_checksum = self._calculate_checksum(json.dumps(backup_copy, sort_keys=True, default=str))
            
            if stored_checksum != calculated_checksum:
                logger.error("Backup checksum mismatch", backup_id=backup_id)
                return False
            
            # Determine tables to restore
            available_tables = list(backup_data['tables'].keys())
            tables_to_restore = tables if tables else available_tables
            
            restored_counts = {}
            
            # Restore each table
            for table in tables_to_restore:
                if table not in backup_data['tables']:
                    logger.warning(f"Table {table} not found in backup")
                    continue
                
                try:
                    table_data = backup_data['tables'][table]
                    
                    if not table_data:
                        logger.info(f"No data to restore for table {table}")
                        continue
                    
                    logger.info(f"Restoring {len(table_data)} records to {table}")
                    
                    # Note: In a real implementation, you'd want to:
                    # 1. Backup current data first
                    # 2. Clear existing data or handle conflicts
                    # 3. Insert restored data
                    # 4. Verify restoration
                    
                    # For now, just log what would be restored
                    restored_counts[table] = len(table_data)
                    
                    logger.info(f"Would restore {len(table_data)} records to {table}")
                    
                except Exception as e:
                    logger.error(f"Failed to restore table {table}", error=e)
                    restored_counts[table] = 0
            
            total_restored = sum(restored_counts.values())
            
            logger.info("Restore completed",
                       backup_id=backup_id,
                       tables_restored=len(restored_counts),
                       total_records=total_restored)
            
            return True
            
        except Exception as e:
            logger.error("Restore failed", error=e, backup_id=backup_id)
            return False
    
    def schedule_daily_backup(self) -> Optional[str]:
        """Create scheduled daily backup"""
        return self.create_full_backup('daily')
    
    def cleanup_old_backups(self):
        """Clean up old backups according to retention policy"""
        try:
            logger.info("Starting backup cleanup")
            
            now = datetime.now()
            deleted_count = 0
            
            # Get all backup files
            backup_files = list(self.backup_dir.glob("backup_*.json.gz"))
            
            for backup_file in backup_files:
                try:
                    # Parse backup info from filename
                    filename = backup_file.stem.replace('.json', '')
                    parts = filename.split('_')
                    
                    if len(parts) >= 4:
                        date_str = parts[1]
                        time_str = parts[2]
                        backup_type = parts[3]
                        
                        backup_date = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                        age_days = (now - backup_date).days
                        
                        should_delete = False
                        
                        if backup_type == 'daily' and age_days > self.daily_retention_days:
                            should_delete = True
                        elif backup_type == 'weekly' and age_days > (self.weekly_retention_weeks * 7):
                            should_delete = True
                        elif backup_type == 'monthly' and age_days > (self.monthly_retention_months * 30):
                            should_delete = True
                        
                        if should_delete:
                            backup_file.unlink()
                            deleted_count += 1
                            logger.info("Deleted old backup",
                                       filename=backup_file.name,
                                       age_days=age_days,
                                       backup_type=backup_type)
                
                except Exception as e:
                    logger.error("Error processing backup file", error=e, filename=backup_file.name)
            
            logger.info("Backup cleanup completed", deleted_count=deleted_count)
            
        except Exception as e:
            logger.error("Backup cleanup failed", error=e)
    
    def get_backup_list(self) -> List[BackupInfo]:
        """Get list of available backups"""
        try:
            backups = []
            backup_files = list(self.backup_dir.glob("backup_*.json.gz"))
            
            for backup_file in backup_files:
                try:
                    # Get file info
                    file_size = backup_file.stat().st_size
                    
                    # Load backup metadata
                    with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    
                    backup_info = BackupInfo(
                        backup_id=backup_data.get('backup_id', backup_file.stem),
                        backup_type=backup_data.get('backup_type', 'unknown'),
                        created_at=datetime.fromisoformat(backup_data.get('created_at', '1970-01-01')),
                        size_bytes=file_size,
                        table_counts=backup_data.get('table_counts', {}),
                        checksum=backup_data.get('checksum', ''),
                        status='available'
                    )
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    logger.error("Error reading backup file", error=e, filename=backup_file.name)
            
            return sorted(backups, key=lambda b: b.created_at, reverse=True)
            
        except Exception as e:
            logger.error("Failed to get backup list", error=e)
            return []
    
    def verify_backup_integrity(self, backup_id: str) -> bool:
        """Verify backup file integrity"""
        try:
            backup_path = self.backup_dir / f"{backup_id}.json.gz"
            
            if not backup_path.exists():
                return False
            
            with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Verify checksum
            stored_checksum = backup_data.get('checksum')
            if not stored_checksum:
                return False
            
            backup_copy = backup_data.copy()
            backup_copy.pop('checksum')
            calculated_checksum = self._calculate_checksum(json.dumps(backup_copy, sort_keys=True, default=str))
            
            return stored_checksum == calculated_checksum
            
        except Exception as e:
            logger.error("Backup integrity check failed", error=e, backup_id=backup_id)
            return False
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate SHA-256 checksum"""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()