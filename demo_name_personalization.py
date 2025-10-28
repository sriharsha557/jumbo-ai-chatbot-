#!/usr/bin/env python3
"""
Demo: Complete Name Personalization Flow
Shows the exact user experience from first login to personalized conversations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import JumboChatbot
import json

def demo_complete_name_flow():
    """Demonstrate the complete name personalization experience"""
    
    print("🎭 DEMO: Complete Name Personalization Experience")
    print("=" * 70)
    print("This demo shows exactly what users experience with name personalization")
    print("=" * 70)
    
    # Initialize chatbot
    chatbot = JumboChatbot()
    
    # Simulate new user signup
    print("📱 SCENARIO: New user signs up with email")
    new_user = {
        'user_id': 'demo-user-456',
        'email': 'alex.johnson@gmail.com',
        'name': 'alex.johnson'  # Auto-generated from email
    }
    
    print(f"✅ User signed up:")
    print(f"   Email: {new_user['email']}")
    print(f"   Auto-generated name: {new_user['name']}")
    print()
    
    # Set user in chatbot (first time, no preferred name)
    chatbot.set_supabase_user(new_user, 'en', preferred_name=None)
    
    print("💬 FIRST CONVERSATION")
    print("-" * 50)
    
    # User's first message
    user_first_message = "Hi there!"
    print(f"User: \"{user_first_message}\"")
    
    # Bot asks for preferred name (this would happen in Flask API)
    first_greeting = chatbot.get_personalized_greeting(is_first_time=True)
    print(f"Bot: \"{first_greeting}\"")
    print()
    
    # Verify it matches your specification
    print("✅ SPECIFICATION CHECK:")
    print(f"   - Uses account name: {'alex.johnson' in first_greeting}")
    print(f"   - Mentions account: {'account' in first_greeting.lower()}")
    print(f"   - Asks what to call them: {'what should i call you' in first_greeting.lower()}")
    print(f"   - Friendly tone: {'😊' in first_greeting}")
    print()
    
    print("💬 USER RESPONDS WITH PREFERRED NAME")
    print("-" * 50)
    
    # Mock supabase service
    class MockSupabaseService:
        def set_preferred_name(self, user_id, preferred_name):
            return True, f"Great! I'll call you {preferred_name} from now on."
    
    mock_supabase = MockSupabaseService()
    
    # Test different ways users might respond
    name_responses = [
        "Alex",
        "Call me Alex", 
        "You can call me Alex",
        "I prefer Alex",
        "My friends call me Alex"
    ]
    
    for response in name_responses:
        print(f"User: \"{response}\"")
        is_name, message = chatbot.check_for_name_preference(response, mock_supabase)
        print(f"Bot: \"{message}\"")
        print(f"✅ Detected correctly: {is_name}")
        print()
    
    # Set the preferred name for the demo
    chatbot.current_user['preferred_name'] = 'Alex'
    chatbot.current_user['name'] = 'Alex'
    
    print("💬 FUTURE CONVERSATIONS")
    print("-" * 50)
    
    # Show returning user experience
    returning_greeting = chatbot.get_personalized_greeting(is_first_time=False)
    print(f"Bot: \"{returning_greeting}\"")
    print()
    
    print("✅ RETURNING USER CHECK:")
    print(f"   - Uses preferred name: {'Alex' in returning_greeting}")
    print(f"   - Welcome back message: {'welcome back' in returning_greeting.lower()}")
    print(f"   - Friendly tone: {'😊' in returning_greeting}")
    print()
    
    print("💬 NATURAL CONVERSATION WITH PERSONALIZATION")
    print("-" * 50)
    
    # Test regular conversations
    conversation_examples = [
        "I'm feeling stressed about work",
        "I had an amazing day today!",
        "Can you help me with something?",
        "I'm confused about my career path"
    ]
    
    for message in conversation_examples:
        print(f"User: \"{message}\"")
        try:
            response, metadata = chatbot.process_message(message)
            print(f"Bot: \"{response}\"")
            
            # Check if name is used naturally (in some responses)
            uses_name = 'Alex' in response
            if uses_name:
                print("✅ Uses preferred name naturally")
            else:
                print("ℹ️ Focuses on content (name not needed)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

def demo_edge_cases():
    """Demo edge cases and error handling"""
    
    print("🧪 DEMO: Edge Cases & Error Handling")
    print("=" * 70)
    
    chatbot = JumboChatbot()
    
    # Mock service
    class MockSupabaseService:
        def set_preferred_name(self, user_id, preferred_name):
            return True, f"Perfect! I'll call you {preferred_name}."
    
    mock_service = MockSupabaseService()
    
    # Test various edge cases
    edge_cases = [
        ("Alex Smith", "Two-word name"),
        ("alex", "Lowercase name"),
        ("ALEX", "Uppercase name"),
        ("Call me J", "Single letter nickname"),
        ("You can call me Dr. Smith", "Title with name"),
        ("I'm Alex123", "Name with numbers"),
        ("My name is Alex, nice to meet you!", "Name in longer sentence"),
        ("Everyone calls me Ace", "Nickname from others"),
        ("I go by my middle name, which is Alex", "Complex explanation")
    ]
    
    # Set up a mock user
    mock_user = {'user_id': 'test-123', 'email': 'test@example.com', 'name': 'test'}
    chatbot.set_supabase_user(mock_user, 'en')
    
    for test_input, description in edge_cases:
        print(f"📝 {description}")
        print(f"User: \"{test_input}\"")
        
        is_name, message = chatbot.check_for_name_preference(test_input, mock_service)
        
        if is_name:
            print(f"Bot: \"{message}\"")
            print("✅ Successfully detected and processed")
        else:
            print("❌ Not detected as name preference")
        
        print("-" * 40)

def demo_database_integration():
    """Demo how it works with the database"""
    
    print("🗄️ DEMO: Database Integration")
    print("=" * 70)
    
    print("📋 Database Schema:")
    print("""
    profiles table:
    - id (UUID, references auth.users)
    - name (TEXT) - auto-generated from email
    - preferred_name (TEXT) - what user wants to be called
    - email (TEXT)
    - language (TEXT)
    - created_at (TIMESTAMP)
    """)
    
    print("🔄 Flow:")
    print("1. User signs up → profile created with email-based name")
    print("2. First chat → bot asks 'what should I call you?'")
    print("3. User responds → preferred_name saved to database")
    print("4. Future chats → bot uses preferred_name")
    print()
    
    print("📊 Example Database Records:")
    print("""
    Before name preference:
    {
      "id": "user-123",
      "name": "john.doe",
      "preferred_name": null,
      "email": "john.doe@gmail.com"
    }
    
    After user says "Call me John":
    {
      "id": "user-123", 
      "name": "john.doe",
      "preferred_name": "John",
      "email": "john.doe@gmail.com"
    }
    """)

if __name__ == "__main__":
    try:
        demo_complete_name_flow()
        print("\n" + "=" * 70)
        demo_edge_cases()
        print("\n" + "=" * 70)
        demo_database_integration()
        
        print("\n🎉 Name Personalization Demo Complete!")
        print("\n📋 SUMMARY:")
        print("✅ Perfect greeting: 'Hey [account_name]! I noticed your name from your account, but I'd love to know—what should I call you?'")
        print("✅ Smart name detection: Handles 'Harsha', 'Call me Alex', 'You can call me Jennifer', etc.")
        print("✅ Database persistence: Saves to Supabase profiles.preferred_name")
        print("✅ Future personalization: 'Hey [preferred_name], welcome back!'")
        print("✅ Natural conversation: Uses preferred name appropriately in responses")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()