# Database package
# Import Database class from the root database.py file
import sys
import os

# Add the parent directory to the path to import database.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the full Database class from database.py
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("database_module", os.path.join(parent_dir, "database.py"))
    database_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(database_module)
    Database = database_module.Database
except Exception as e:
    print(f"Warning: Could not import Database from database.py: {e}")
    # Fallback: create a minimal Database class with all required methods
    from typing import Dict, List, Optional, Tuple
    from datetime import datetime
    import json
    
    class Database:
        def __init__(self, data_dir="./jumbo_data"):
            self.data_dir = data_dir
            os.makedirs(data_dir, exist_ok=True)
        
        def register_user(self, name, language="en"):
            return True, f"User {name} registered"
        
        def get_user(self, name):
            return {"name": name, "language": "en"}
        
        def update_user_activity(self, name):
            pass
        
        def save_conversation(self, name: str, user_message: str, bot_response: str, 
                             mood: str = "neutral", metadata: Dict = None):
            """Save conversation exchange - fallback implementation"""
            return True
        
        def load_conversations(self, name: str) -> List[Dict]:
            """Load conversations - fallback implementation"""
            return []
        
        def get_recent_conversations(self, name: str, limit: int = 5) -> List[Dict]:
            """Get recent conversations - fallback implementation"""
            return []