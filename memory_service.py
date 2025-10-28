"""
memory_service.py - Enhanced Memory Management with Conversation Context
Stores relationships, preferences, and conversation history
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from collections import defaultdict
import hashlib

class MemoryService:
    """Manage user memories and relationships"""
    
    def __init__(self, data_dir: str = "./user_memories"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def _get_memory_file(self, user_name: str) -> str:
        """Get memory file path for user"""
        safe_name = hashlib.md5(user_name.encode()).hexdigest()
        return os.path.join(self.data_dir, f"{safe_name}_memory.json")
    
    def _load_memory(self, user_name: str) -> Dict:
        """Load user memory"""
        memory_file = self._get_memory_file(user_name)
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return self._create_empty_memory()
    
    def _create_empty_memory(self) -> Dict:
        """Create empty memory structure"""
        return {
            "people": {},  # Friends, family, colleagues
            "preferences": {},  # Food, music, activities
            "events": [],  # Important dates, milestones
            "moods": [],  # Mood history for context
            "topics": defaultdict(list),  # Topics user discusses
            "last_updated": None,
            "created_at": datetime.now().isoformat()
        }
    
    def _save_memory(self, user_name: str, memory: Dict):
        """Save user memory"""
        memory["last_updated"] = datetime.now().isoformat()
        memory_file = self._get_memory_file(user_name)
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2, default=str)
    
    def extract_relationships(self, user_name: str, text: str) -> List[str]:
        """Extract mentioned people from conversation"""
        memory = self._load_memory(user_name)
        
        # Keywords that indicate relationships
        relationship_indicators = {
            "friend": "friend",
            "best friend": "best_friend",
            "brother": "brother",
            "sister": "sister",
            "mother": "mother",
            "father": "father",
            "mom": "mother",
            "dad": "father",
            "girlfriend": "girlfriend",
            "boyfriend": "boyfriend",
            "wife": "wife",
            "husband": "husband",
            "colleague": "colleague",
            "coworker": "colleague",
            "mentor": "mentor",
            "teacher": "teacher"
        }
        
        text_lower = text.lower()
        extracted = []
        
        for indicator, rel_type in relationship_indicators.items():
            if indicator in text_lower:
                # Try to extract name after indicator
                idx = text_lower.find(indicator)
                after_indicator = text[idx + len(indicator):].strip()
                
                # Get first word as name (simple approach)
                words = after_indicator.split()
                if words and len(words[0]) > 1:
                    name = words[0].rstrip('.,!?').title()
                    extracted.append({
                        "name": name,
                        "relationship": rel_type,
                        "mentioned_at": datetime.now().isoformat()
                    })
        
        # Save relationships
        if extracted:
            for person in extracted:
                if person["name"] not in memory["people"]:
                    memory["people"][person["name"]] = person
            self._save_memory(user_name, memory)
        
        return extracted
    
    def get_best_friends(self, user_name: str) -> List[str]:
        """Get list of best friends"""
        memory = self._load_memory(user_name)
        friends = [
            name for name, info in memory["people"].items()
            if info.get("relationship") in ["best_friend", "friend"]
        ]
        return friends
    
    def get_all_people(self, user_name: str) -> Dict:
        """Get all known people"""
        memory = self._load_memory(user_name)
        return memory.get("people", {})
    
    def add_preference(self, user_name: str, category: str, value: str):
        """Add user preference"""
        memory = self._load_memory(user_name)
        if category not in memory["preferences"]:
            memory["preferences"][category] = []
        if value not in memory["preferences"][category]:
            memory["preferences"][category].append(value)
        self._save_memory(user_name, memory)
    
    def get_preferences(self, user_name: str, category: str = None) -> Dict:
        """Get user preferences"""
        memory = self._load_memory(user_name)
        prefs = memory.get("preferences", {})
        if category:
            return {category: prefs.get(category, [])}
        return prefs
    
    def record_mood(self, user_name: str, mood: str, confidence: float):
        """Record mood for analysis"""
        memory = self._load_memory(user_name)
        memory["moods"].append({
            "mood": mood,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 100 moods
        memory["moods"] = memory["moods"][-100:]
        self._save_memory(user_name, memory)
    
    def get_mood_trends(self, user_name: str, days: int = 7) -> Dict:
        """Get mood trends over time"""
        memory = self._load_memory(user_name)
        moods = memory.get("moods", [])
        
        cutoff = datetime.now() - timedelta(days=days)
        recent_moods = [
            m for m in moods 
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]
        
        mood_counts = defaultdict(int)
        for m in recent_moods:
            mood_counts[m["mood"]] += 1
        
        return dict(mood_counts)
    
    def add_memory_note(self, user_name: str, topic: str, content: str):
        """Add a conversation note"""
        memory = self._load_memory(user_name)
        if topic not in memory["topics"]:
            memory["topics"][topic] = []
        
        memory["topics"][topic].append({
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save_memory(user_name, memory)
    
    def get_conversation_context(self, user_name: str, max_days: int = 7) -> str:
        """Generate context from past conversations"""
        memory = self._load_memory(user_name)
        
        context_parts = []
        
        # Add recent people mentioned
        if memory["people"]:
            friends = self.get_best_friends(user_name)
            if friends:
                context_parts.append(f"Best friends: {', '.join(friends)}")
            
            all_people = self.get_all_people(user_name)
            if all_people:
                context_parts.append(f"Known people: {', '.join(list(all_people.keys())[:5])}")
        
        # Add preferences
        if memory["preferences"]:
            prefs = self.get_preferences(user_name)
            pref_str = "; ".join([f"{k}: {', '.join(v)}" for k, v in prefs.items()])
            if pref_str:
                context_parts.append(f"Preferences: {pref_str}")
        
        # Add mood trends
        trends = self.get_mood_trends(user_name, max_days)
        if trends:
            mood_str = ", ".join([f"{m}: {c} times" for m, c in trends.items()])
            context_parts.append(f"Recent moods: {mood_str}")
        
        # Add recent topics
        if memory["topics"]:
            recent_topics = list(memory["topics"].keys())[:3]
            context_parts.append(f"Recent topics: {', '.join(recent_topics)}")
        
        return " | ".join(context_parts) if context_parts else ""
    
    def create_memory_summary(self, user_name: str) -> str:
        """Create a summary for system prompt"""
        context = self.get_conversation_context(user_name)
        memory = self._load_memory(user_name)
        
        summary = f"""
MEMORY OF {user_name}:
{context}

Remember to:
- Ask about their best friends: {', '.join(self.get_best_friends(user_name)) or 'Not known yet'}
- Use their preferences when relevant
- Acknowledge their mood patterns
- Continue conversations from yesterday/last week if relevant
"""
        return summary.strip()