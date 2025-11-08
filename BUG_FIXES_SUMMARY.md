# Bug Fixes Summary

## Issues Fixed

### 1. ✅ Name Extraction Bug - "Hello Jumbo" → "Feeling Struck"

**Problem:** 
- Jumbo was trying to extract names from greetings like "Hello Jumbo"
- Somehow extracting weird names like "Feeling Struck"

**Root Cause:**
- Name extraction was too aggressive
- Greeting detection wasn't comprehensive enough
- No validation for common words being used as names

**Solution:**
- Added comprehensive excluded phrases list (greetings, common phrases)
- Added "Hello Jumbo", "Hi Jumbo", "Hey Jumbo" specifically
- Added validation to reject common words like "feeling", "struck", "good", etc.
- Improved pattern matching to be more strict
- Only extracts names when explicit patterns like "call me", "my name is" are present

**Files Changed:**
- `chatbot.py` - Enhanced `check_for_name_preference()` method

---

### 2. ✅ Conversation Lost on Tab Switch (MAJOR)

**Problem:**
- When switching browser tabs, all conversation history was lost
- Had to start over every time

**Root Cause:**
- `conversationHistory` state was initialized as empty array `[]`
- Never loaded from backend
- Component state was lost on unmount (tab switch)

**Solution:**
- Added `useEffect` hook to load conversation history on component mount
- Fetches last 20 messages from backend API
- Converts backend format to chat format
- Persists across tab switches

**Files Changed:**
- `jumbo-ui/src/components/ChatPage.jsx` - Added conversation history loading

---

## Testing Checklist

### Name Extraction:
- [ ] Say "Hello Jumbo" → Should NOT extract name
- [ ] Say "Hi there" → Should NOT extract name  
- [ ] Say "Call me Harsha" → Should extract "Harsha"
- [ ] Say "My name is John" → Should extract "John"
- [ ] Say "I'm feeling good" → Should NOT extract "Feeling Good"

### Conversation Persistence:
- [ ] Start a conversation
- [ ] Switch to another tab
- [ ] Switch back
- [ ] Conversation should still be visible
- [ ] Send another message
- [ ] Should continue the conversation

---

## How It Works Now

### First Time User Flow:
1. User logs in (no preferred_name)
2. Jumbo asks: "What should I call you?"
3. User says: "Call me Harsha"
4. Jumbo extracts "Harsha" and saves it
5. Jumbo confirms: "Great! I'll call you Harsha"

### Returning User Flow:
1. User logs in (has preferred_name)
2. User says: "Hello Jumbo"
3. Jumbo responds normally (no name extraction)
4. Conversation continues

### Tab Switch:
1. User has conversation with Jumbo
2. User switches to another tab
3. User switches back
4. Conversation history loads from backend
5. User can continue where they left off

---

## Technical Details

### Name Extraction Logic:
```python
# 1. Check excluded phrases first
if message in ['hello jumbo', 'hi', 'hey', ...]:
    return False  # Don't extract

# 2. Check for explicit patterns
if 'call me' in message or 'my name is' in message:
    # Extract name
    
# 3. Validate extracted name
if name in ['feeling', 'struck', 'good', ...]:
    return False  # Reject common words
```

### Conversation Loading:
```javascript
useEffect(() => {
  // Load on mount
  fetch('/api/v1/chat/history?limit=20')
    .then(data => setConversationHistory(data))
}, [currentUser]);
```

---

## Known Limitations

1. **Conversation history limit**: Only loads last 20 messages
2. **Name validation**: Limited to common words, may need expansion
3. **Multi-word names**: Limited to 2 words maximum

---

## Future Improvements

1. **Infinite scroll**: Load more history as user scrolls up
2. **Search conversations**: Find specific past conversations
3. **Export conversations**: Download chat history
4. **Better name validation**: Use NLP to detect actual names vs words
5. **Conversation summaries**: Show brief summary of past chats

---

## Deployment Notes

After deploying these changes:
1. Clear browser cache
2. Test name extraction with various inputs
3. Test tab switching multiple times
4. Monitor backend logs for any errors
5. Check conversation history API performance

---

## Support

If issues persist:
1. Check browser console for errors
2. Check backend logs
3. Verify Supabase connection
4. Test with different browsers
5. Clear localStorage and try again
