"""
database.py - Handle all database operations
User profiles, conversation memory, and unique name validation
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

class Database:
    """Manage user data and conversation history"""
    
    def __init__(self, data_dir: str = "./jumbo_data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.conversations_dir = os.path.join(data_dir, "conversations")
        
        # Create directories if they don't exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(self.conversations_dir, exist_ok=True)
        
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load all registered users"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading users: {e}")
                return {}
        return {}
    
    def _save_users(self):
        """Save users to file"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def name_exists(self, name: str) -> bool:
        """Check if name is already registered"""
        return name.lower() in {n.lower() for n in self.users.keys()}
    
    def register_user(self, name: str, language: str = "te") -> Tuple[bool, str]:
        """
        Register a new user
        Returns: (success: bool, message: str)
        """
        if self.name_exists(name):
            return False, f"'{name}' name is already taken. Please use a different name."
        
        try:
            self.users[name] = {
                "language": language,
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "user_id": self._generate_user_id(name)
            }
            self._save_users()
            return True, f"Welcome {name}! Your profile has been created."
        except Exception as e:
            return False, f"Error registering user: {e}"
    
    def _generate_user_id(self, name: str) -> str:
        """Generate unique user ID"""
        return hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()
    
    def get_user(self, name: str) -> Optional[Dict]:
        """Get user profile"""
        for user_name, user_data in self.users.items():
            if user_name.lower() == name.lower():
                return {
                    "name": user_name,
                    **user_data
                }
        return None
    
    def update_user_activity(self, name: str):
        """Update last active time"""
        user = self.get_user(name)
        if user:
            self.users[user["name"]]["last_active"] = datetime.now().isoformat()
            self._save_users()
    
    # ========================================================================
    # CONVERSATION MEMORY
    # ========================================================================
    
    def _get_user_conv_file(self, name: str) -> str:
        """Get conversation file path for user"""
        user = self.get_user(name)
        if user:
            return os.path.join(self.conversations_dir, f"{user['user_id']}_conversations.json")
        return None
    
    def load_conversations(self, name: str) -> List[Dict]:
        """Load all conversations for a user"""
        conv_file = self._get_user_conv_file(name)
        if conv_file and os.path.exists(conv_file):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading conversations: {e}")
                return []
        return []
    
    def save_conversation(self, name: str, user_message: str, bot_response: str, 
                         mood: str = "neutral", metadata: Dict = None):
        """Save conversation exchange"""
        conv_file = self._get_user_conv_file(name)
        if not conv_file:
            return False
        
        try:
            conversations = self.load_conversations(name)
            
            exchange = {
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "bot_response": bot_response,
                "mood": mood,
                "metadata": metadata or {}
            }
            
            conversations.append(exchange)
            
            # Keep last 100 conversations
            if len(conversations) > 100:
                conversations = conversations[-100:]
            
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def get_recent_conversations(self, name: str, limit: int = 5) -> List[Dict]:
        """Get recent conversations for context"""
        conversations = self.load_conversations(name)
        return conversations[-limit:] if conversations else []
    
    def get_conversation_summary(self, name: str) -> str:
        """Generate summary of past conversations"""
        conversations = self.get_recent_conversations(name, limit=10)
        
        if not conversations:
            return "No previous conversations."
        
        summary = "Recent conversations:\n"
        for i, conv in enumerate(conversations[-5:], 1):
            user_msg = conv.get('user_message', '')[:50]
            summary += f"{i}. You: {user_msg}...\n"
        
        return summary
    
    def get_all_users(self) -> List[str]:
        """Get all registered user names"""
        return list(self.users.keys())
    
    def user_count(self) -> int:
        """Get total number of users"""
        return len(self.users)