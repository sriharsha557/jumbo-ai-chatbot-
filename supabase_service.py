"""
Supabase Service for Jumbo Chatbot
Handles authentication and data storage using Supabase
Matches the provided database schema exactly
"""

import os
from typing import Dict, List, Optional, Tuple, Any
from supabase import create_client, Client
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_ANON_KEY')
        self.service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(self.url, self.key)
        
        # Service role client for admin operations
        if self.service_key:
            self.admin_client: Client = create_client(self.url, self.service_key)
        else:
            self.admin_client = self.supabase
            logger.warning("SUPABASE_SERVICE_ROLE_KEY not set, using anon key for admin operations")
        
        self.current_user_id = None

    # ==================== AUTHENTICATION ====================
    
    def sign_up(self, email: str, password: str, user_data: Dict = None) -> Tuple[bool, str, Dict]:
        """Sign up a new user"""
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            
            if response.user:
                return True, "User created successfully", {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at
                }
            else:
                return False, "Failed to create user", {}
                
        except Exception as e:
            logger.error(f"Sign up error: {e}")
            return False, str(e), {}

    def sign_in(self, email: str, password: str) -> Tuple[bool, str, Dict]:
        """Sign in existing user"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return True, "Login successful", {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token
                }
            else:
                return False, "Invalid credentials", {}
                
        except Exception as e:
            logger.error(f"Sign in error: {e}")
            return False, str(e), {}

    def sign_out(self) -> Tuple[bool, str]:
        """Sign out current user"""
        try:
            self.supabase.auth.sign_out()
            return True, "Signed out successfully"
        except Exception as e:
            logger.error(f"Sign out error: {e}")
            return False, str(e)

    def get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user"""
        try:
            user = self.supabase.auth.get_user()
            if user and user.user:
                return {
                    "user_id": user.user.id,
                    "email": user.user.email,
                    "created_at": user.user.created_at,
                    "user_metadata": user.user.user_metadata
                }
            return None
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
    
    def get_current_user_from_token(self, access_token: str) -> Optional[Dict]:
        """Get current user from access token"""
        try:
            # Validate the token with Supabase
            user_response = self.supabase.auth.get_user(access_token)
            if user_response and user_response.user:
                user = user_response.user
                return {
                    "user_id": user.id,
                    "email": user.email,
                    "created_at": user.created_at,
                    "user_metadata": user.user_metadata
                }
            return None
        except Exception as e:
            logger.error(f"Get user from token error: {e}")
            return None

    # ==================== USER PROFILES ====================
    
    def create_user_profile(self, user_id: str, profile_data: Dict) -> Tuple[bool, str]:
        """Create user profile in profiles table"""
        try:
            data = {
                "id": user_id,  # Use 'id' not 'user_id' to match schema
                "created_at": datetime.utcnow().isoformat(),
                **profile_data
            }
            
            # Use admin client to bypass RLS for profile creation
            response = self.admin_client.table('profiles').insert(data).execute()
            
            if response.data:
                return True, "Profile created successfully"
            else:
                return False, "Failed to create profile"
                
        except Exception as e:
            logger.error(f"Create profile error: {e}")
            return False, str(e)

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile by user_id"""
        try:
            # Use admin client to bypass RLS for profile reading in backend operations
            response = self.admin_client.table('profiles').select("*").eq('id', user_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Get profile error: {e}")
            return None

    def update_user_profile(self, user_id: str, updates: Dict) -> Tuple[bool, str]:
        """Update user profile"""
        try:
            response = self.supabase.table('profiles').update(updates).eq('id', user_id).execute()
            
            if response.data:
                return True, "Profile updated successfully"
            else:
                return False, "Failed to update profile"
                
        except Exception as e:
            logger.error(f"Update profile error: {e}")
            return False, str(e)

    def set_preferred_name(self, user_id: str, preferred_name: str) -> Tuple[bool, str]:
        """Set user's preferred name"""
        try:
            response = (self.supabase.table('profiles')
                       .update({'preferred_name': preferred_name})
                       .eq('id', user_id)
                       .execute())
            
            if response.data:
                return True, f"Great! I'll call you {preferred_name} from now on."
            else:
                return False, "Failed to save your preferred name"
                
        except Exception as e:
            logger.error(f"Set preferred name error: {e}")
            return False, str(e)

    def get_preferred_name(self, user_id: str) -> Optional[str]:
        """Get user's preferred name"""
        try:
            profile = self.get_user_profile(user_id)
            return profile.get('preferred_name') if profile else None
        except Exception as e:
            logger.error(f"Get preferred name error: {e}")
            return None

    # ==================== CONVERSATIONS ====================
    
    def save_conversation(self, user_id: str, conversation_data: Dict) -> Tuple[bool, str, str]:
        """Save conversation to database matching schema"""
        try:
            # Use service role client for admin operations to bypass RLS
            metadata = conversation_data.get('metadata', {})
            
            data = {
                "user_id": user_id,
                "user_message": conversation_data.get('message', ''),
                "bot_response": conversation_data.get('response', ''),
                "mood": metadata.get('mood', 'neutral'),
                "mood_confidence": metadata.get('mood_confidence', 0.0),
                "detected_language": metadata.get('language', 'en'),
                "used_llm": metadata.get('used_llm', False),
                "scenario": metadata.get('scenario', 'general'),
                "metadata": metadata
            }
            
            # Use admin client to bypass RLS for now
            response = self.admin_client.table('conversations').insert(data).execute()
            
            if response.data and len(response.data) > 0:
                conversation_id = response.data[0]['id']
                
                # Also save mood history
                self.save_mood_history(user_id, {
                    'mood': data['mood'],
                    'confidence': data['mood_confidence'],
                    'context': f"Conversation: {conversation_data.get('message', '')[:50]}..."
                })
                
                return True, "Conversation saved", conversation_id
            else:
                return False, "Failed to save conversation", ""
                
        except Exception as e:
            logger.error(f"Save conversation error: {e}")
            return False, str(e), ""

    def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's conversation history"""
        try:
            response = (self.supabase.table('conversations')
                       .select("*")
                       .eq('user_id', user_id)
                       .order('created_at', desc=True)
                       .limit(limit)
                       .execute())
            
            conversations = []
            for conv in response.data:
                conversations.append({
                    "id": conv['id'],
                    "message": conv['user_message'],
                    "response": conv['bot_response'],
                    "mood": conv['mood'],
                    "mood_confidence": conv['mood_confidence'],
                    "language": conv['detected_language'],
                    "used_llm": conv['used_llm'],
                    "scenario": conv['scenario'],
                    "metadata": conv['metadata'] if conv['metadata'] else {},
                    "created_at": conv['created_at']
                })
            
            return conversations
            
        except Exception as e:
            logger.error(f"Get conversations error: {e}")
            return []

    def delete_conversation(self, conversation_id: str, user_id: str) -> Tuple[bool, str]:
        """Delete a specific conversation"""
        try:
            response = (self.supabase.table('conversations')
                       .delete()
                       .eq('id', conversation_id)
                       .eq('user_id', user_id)
                       .execute())
            
            if response.data:
                return True, "Conversation deleted"
            else:
                return False, "Conversation not found or access denied"
                
        except Exception as e:
            logger.error(f"Delete conversation error: {e}")
            return False, str(e)

    # ==================== USER MEMORIES ====================
    
    def save_user_memory(self, user_id: str, memory_type: str, memory_data: Dict) -> Tuple[bool, str]:
        """Save user memory matching enhanced schema structure"""
        try:
            data = {
                "user_id": user_id,
                "memory_type": memory_type,  # 'person', 'preference', 'event', 'topic', 'fact', 'emotion'
                "category": memory_data.get('category'),
                "fact": memory_data.get('fact', ''),  # The actual memory
                "name": memory_data.get('name'),
                "relationship": memory_data.get('relationship'),
                "importance_score": memory_data.get('importance_score', 1.0),
                "data": memory_data
            }
            
            response = self.supabase.table('user_memories').insert(data).execute()
            
            if response.data:
                return True, "Memory saved successfully"
            else:
                return False, "Failed to save memory"
                
        except Exception as e:
            logger.error(f"Save memory error: {e}")
            return False, str(e)

    def search_user_memories(self, user_id: str, search_terms: List[str], memory_types: List[str] = None) -> List[Dict]:
        """Search user memories by keywords and types"""
        try:
            query = self.supabase.table('user_memories').select("*").eq('user_id', user_id)
            
            if memory_types:
                query = query.in_('memory_type', memory_types)
            
            response = query.order('importance_score', desc=True).limit(10).execute()
            
            if not response.data:
                return []
            
            # Filter by search terms (simple text matching)
            filtered_memories = []
            for memory in response.data:
                fact_lower = memory.get('fact', '').lower()
                name_lower = (memory.get('name') or '').lower()
                category_lower = (memory.get('category') or '').lower()
                
                # Check if any search term matches
                for term in search_terms:
                    term_lower = term.lower()
                    if (term_lower in fact_lower or 
                        term_lower in name_lower or 
                        term_lower in category_lower):
                        filtered_memories.append(memory)
                        break
            
            return filtered_memories[:5]  # Return top 5 matches
            
        except Exception as e:
            logger.error(f"Search memories error: {e}")
            return []

    def get_memories_by_category(self, user_id: str, category: str, limit: int = 5) -> List[Dict]:
        """Get memories by specific category"""
        try:
            response = (self.supabase.table('user_memories')
                       .select("*")
                       .eq('user_id', user_id)
                       .eq('category', category)
                       .order('importance_score', desc=True)
                       .limit(limit)
                       .execute())
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Get memories by category error: {e}")
            return []

    def get_user_memories(self, user_id: str, memory_type: str = None) -> List[Dict]:
        """Get user memories by type"""
        try:
            query = self.supabase.table('user_memories').select("*").eq('user_id', user_id)
            
            if memory_type:
                query = query.eq('memory_type', memory_type)
            
            response = query.order('updated_at', desc=True).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Get memories error: {e}")
            return []

    def update_user_memory(self, memory_id: str, user_id: str, updates: Dict) -> Tuple[bool, str]:
        """Update existing memory"""
        try:
            response = (self.supabase.table('user_memories')
                       .update(updates)
                       .eq('id', memory_id)
                       .eq('user_id', user_id)
                       .execute())
            
            if response.data:
                return True, "Memory updated successfully"
            else:
                return False, "Memory not found or access denied"
                
        except Exception as e:
            logger.error(f"Update memory error: {e}")
            return False, str(e)

    # ==================== MOOD HISTORY ====================
    
    def save_mood_history(self, user_id: str, mood_data: Dict) -> Tuple[bool, str]:
        """Save mood history entry"""
        try:
            data = {
                "user_id": user_id,
                "mood": mood_data.get('mood', 'neutral'),
                "confidence": mood_data.get('confidence', 0.0),
                "context": mood_data.get('context', '')
            }
            
            # Use admin client to bypass RLS for mood history
            response = self.admin_client.table('mood_history').insert(data).execute()
            
            if response.data:
                return True, "Mood history saved"
            else:
                return False, "Failed to save mood history"
                
        except Exception as e:
            logger.error(f"Save mood history error: {e}")
            return False, str(e)

    def get_mood_history(self, user_id: str, limit: int = 30) -> List[Dict]:
        """Get user's mood history"""
        try:
            response = (self.supabase.table('mood_history')
                       .select("*")
                       .eq('user_id', user_id)
                       .order('created_at', desc=True)
                       .limit(limit)
                       .execute())
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Get mood history error: {e}")
            return []

    # ==================== ANALYTICS ====================
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
        try:
            # Count conversations
            conv_response = (self.supabase.table('conversations')
                           .select("id", count="exact")
                           .eq('user_id', user_id)
                           .execute())
            
            conversation_count = conv_response.count if conv_response.count else 0
            
            # Get first conversation date
            first_conv = (self.supabase.table('conversations')
                         .select("created_at")
                         .eq('user_id', user_id)
                         .order('created_at', desc=False)
                         .limit(1)
                         .execute())
            
            first_conversation_date = None
            if first_conv.data and len(first_conv.data) > 0:
                first_conversation_date = first_conv.data[0]['created_at']
            
            return {
                "total_conversations": conversation_count,
                "first_conversation": first_conversation_date,
                "user_since": first_conversation_date
            }
            
        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return {
                "total_conversations": 0,
                "first_conversation": None,
                "user_since": None
            }

    # ==================== ADMIN FUNCTIONS ====================
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin function)"""
        try:
            response = self.admin_client.table('profiles').select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Get all users error: {e}")
            return []

    def delete_user_data(self, user_id: str) -> Tuple[bool, str]:
        """Delete all user data (admin function)"""
        try:
            # Delete conversations
            self.admin_client.table('conversations').delete().eq('user_id', user_id).execute()
            
            # Delete memories
            self.admin_client.table('user_memories').delete().eq('user_id', user_id).execute()
            
            # Delete profile
            self.admin_client.table('profiles').delete().eq('id', user_id).execute()
            
            return True, "User data deleted successfully"
            
        except Exception as e:
            logger.error(f"Delete user data error: {e}")
            return False, str(e)