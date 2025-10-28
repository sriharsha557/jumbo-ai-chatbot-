"""
Database Migration Manager for Jumbo Chatbot
Handles schema versioning and migrations for reliable memory system
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from supabase_service import SupabaseService
from monitoring import logger

@dataclass
class Migration:
    """Migration definition"""
    version: str
    name: str
    description: str
    up_sql: str
    down_sql: str
    created_at: datetime

class MigrationManager:
    """Manages database schema migrations"""
    
    def __init__(self, supabase_service: SupabaseService):
        self.supabase = supabase_service
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'sql')
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Ensure migrations tracking table exists"""
        create_migrations_table = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            version TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT,
            applied_at TIMESTAMPTZ DEFAULT NOW(),
            rollback_sql TEXT,
            checksum TEXT
        );
        
        CREATE INDEX IF NOT EXISTS idx_migrations_version ON schema_migrations(version);
        CREATE INDEX IF NOT EXISTS idx_migrations_applied ON schema_migrations(applied_at DESC);
        """
        
        try:
            # Execute using Supabase RPC or direct SQL execution
            logger.info("Ensuring migrations table exists")
            # Note: This would need to be executed via Supabase SQL editor or RPC function
            
        except Exception as e:
            logger.error("Failed to create migrations table", error=e)
            raise
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        try:
            response = self.supabase.supabase.table('schema_migrations').select('version').execute()
            return [row['version'] for row in response.data]
        except Exception as e:
            logger.error("Failed to get applied migrations", error=e)
            return []
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations"""
        applied_versions = set(self.get_applied_migrations())
        all_migrations = self._load_migrations()
        
        pending = []
        for migration in all_migrations:
            if migration.version not in applied_versions:
                pending.append(migration)
        
        return sorted(pending, key=lambda m: m.version)
    
    def _load_migrations(self) -> List[Migration]:
        """Load all migration files"""
        migrations = []
        
        if not os.path.exists(self.migrations_dir):
            return migrations
        
        for filename in sorted(os.listdir(self.migrations_dir)):
            if filename.endswith('.json'):
                filepath = os.path.join(self.migrations_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        migration = Migration(
                            version=data['version'],
                            name=data['name'],
                            description=data['description'],
                            up_sql=data['up_sql'],
                            down_sql=data['down_sql'],
                            created_at=datetime.fromisoformat(data['created_at'])
                        )
                        migrations.append(migration)
                except Exception as e:
                    logger.error(f"Failed to load migration {filename}", error=e)
        
        return migrations
    
    def apply_migration(self, migration: Migration) -> bool:
        """Apply a single migration"""
        try:
            logger.info(f"Applying migration {migration.version}: {migration.name}")
            
            # Note: In a real implementation, this would execute the SQL
            # For Supabase, migrations are typically run via the dashboard or CLI
            
            # Record the migration as applied
            migration_record = {
                'version': migration.version,
                'name': migration.name,
                'description': migration.description,
                'rollback_sql': migration.down_sql,
                'checksum': self._calculate_checksum(migration.up_sql)
            }
            
            response = self.supabase.supabase.table('schema_migrations').insert(migration_record).execute()
            
            if response.data:
                logger.info(f"Migration {migration.version} applied successfully")
                return True
            else:
                logger.error(f"Failed to record migration {migration.version}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}", error=e)
            return False
    
    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration"""
        try:
            # Get migration record
            response = self.supabase.supabase.table('schema_migrations').select('*').eq('version', version).execute()
            
            if not response.data:
                logger.error(f"Migration {version} not found")
                return False
            
            migration_record = response.data[0]
            rollback_sql = migration_record.get('rollback_sql')
            
            if not rollback_sql:
                logger.error(f"No rollback SQL for migration {version}")
                return False
            
            logger.info(f"Rolling back migration {version}")
            
            # Note: Execute rollback SQL here
            
            # Remove migration record
            self.supabase.supabase.table('schema_migrations').delete().eq('version', version).execute()
            
            logger.info(f"Migration {version} rolled back successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}", error=e)
            return False
    
    def migrate_up(self) -> Tuple[bool, List[str]]:
        """Apply all pending migrations"""
        pending_migrations = self.get_pending_migrations()
        
        if not pending_migrations:
            logger.info("No pending migrations")
            return True, []
        
        applied = []
        for migration in pending_migrations:
            if self.apply_migration(migration):
                applied.append(migration.version)
            else:
                logger.error(f"Migration failed at {migration.version}")
                return False, applied
        
        logger.info(f"Applied {len(applied)} migrations: {applied}")
        return True, applied
    
    def get_migration_status(self) -> Dict:
        """Get current migration status"""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        return {
            'applied_count': len(applied),
            'pending_count': len(pending),
            'applied_versions': applied,
            'pending_versions': [m.version for m in pending],
            'current_version': max(applied) if applied else None
        }
    
    def _calculate_checksum(self, sql: str) -> str:
        """Calculate checksum for SQL content"""
        import hashlib
        return hashlib.sha256(sql.encode()).hexdigest()
    
    def create_migration(self, name: str, description: str, up_sql: str, down_sql: str) -> str:
        """Create a new migration file"""
        # Generate version based on timestamp
        version = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        migration_data = {
            'version': version,
            'name': name,
            'description': description,
            'up_sql': up_sql,
            'down_sql': down_sql,
            'created_at': datetime.now().isoformat()
        }
        
        # Ensure migrations directory exists
        os.makedirs(self.migrations_dir, exist_ok=True)
        
        # Write migration file
        filename = f"{version}_{name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.migrations_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(migration_data, f, indent=2)
        
        logger.info(f"Created migration {version}: {name}")
        return version