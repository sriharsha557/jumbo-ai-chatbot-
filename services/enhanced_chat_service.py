"""
Enhanced Chat Service - Simplified version for testing
"""

from typing import Dict, List, Tuple, Optional, Any
from services.chat_service import ChatService

class EnhancedChatService:
    """Simplified enhanced chat service for testing"""
    
    def __init__(self, supabase_service, llm_service=None):
        # Use the existing chat service as fallback
        self.chat_service = ChatService(supabase_service)
        self.supabase_service = supabase_service
    
    def process_message(self, user_id: str, message: str, 
                       conversation_context: List[Dict] = None,
                       emotion: str = None) -> Tuple[str, Dict[str, Any]]:
        """Process message using existing chat service"""
        return self.chat_service.process_message(user_id, message, conversation_context, emotion)
    
    def get_conversation_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get conversation history"""
        return self.chat_service.get_conversation_history(user_id, limit)
    
    def get_user_memories(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user memories"""
        return self.chat_service.get_user_memories(user_id, limit)
    
    def get_enhanced_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'system_status': 'operational',
            'total_conversations_processed': 0,
            'average_response_time_ms': 200,
            'average_quality_score': 0.8,
            'strategy_distribution': {'chat_service': 100},
            'fallback_usage_rate': 0,
            'system_components': {
                'chat_service': 'active'
            }
        }

def create_enhanced_chat_service(supabase_service, llm_service=None):
    """Factory function to create enhanced chat service"""
    return EnhancedChatService(supabase_service, llm_service)