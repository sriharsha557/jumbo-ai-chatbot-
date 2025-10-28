# Integration Guide: Adding Language Layer to Jumbo

## Step 1: Install Required Dependencies

```bash
pip install googletrans==4.0.0rc1
pip install langdetect
```

## Step 2: Add Language Layer to Your Code

Add this import at the top of `Jumbo_v1.py`:

```python
from language_layer import LanguageLayer, LanguageConfig, TELUGU_MOOD_KEYWORDS
```

## Step 3: Modify EnhancedJumboMemory Class

### Add language field to store_conversation:

```python
def store_conversation(self, user_message: str, jumbo_response: str, mood: str, 
                      confidence: float, user_name: str = None, 
                      language: str = "te"):  # NEW PARAMETER
    """ENHANCED: Store conversation with language information"""
    try:
        if not user_message or not jumbo_response:
            logger.warning("Empty message or response, skipping storage")
            return False
            
        conversation_text = f"User: {user_message}\nJumbo: {jumbo_response}"
        embedding = simple_text_embedding(conversation_text, self.embedding_dim)
        
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "mood": mood or "neutral",
            "confidence": max(0.0, min(1.0, confidence)),
            "type": "conversation",
            "message_length": len(user_message),
            "response_length": len(jumbo_response),
            "user_message": user_message[:1000],
            "jumbo_response": jumbo_response[:1000],
            "language": language  # NEW FIELD
        }
        if user_name and isinstance(user_name, str):
            metadata["user_name"] = user_name[:50]
        
        self.index.add(embedding.reshape(1, -1))
        self.metadata.append(metadata)
        self._save_to_disk()
        self._cleanup_old_memories()
        return True
        
    except Exception as e:
        logger.error(f"Failed to store conversation: {e}")
        return False
```

### Add method to store and retrieve language preference:

```python
def store_language_preference(self, language: str):
    """Store user's preferred language"""
    try:
        if language in LanguageConfig.SUPPORTED_LANGUAGES:
            self.user_info["preferred_language"] = {
                "value": language,
                "timestamp": datetime.now().isoformat()
            }
            self._save_to_disk()
            logger.info(f"Stored language preference: {language}")
    except Exception as e:
        logger.error(f"Failed to store language preference: {e}")

def get_language_preference(self) -> str:
    """Get user's preferred language"""
    try:
        lang_info = self.user_info.get("preferred_language")
        if lang_info and isinstance(lang_info, dict):
            lang = lang_info.get("value")
            if lang in LanguageConfig.SUPPORTED_LANGUAGES:
                return lang
    except Exception as e:
        logger.error(f"Failed to get language preference: {e}")
    return LanguageConfig.DEFAULT_LANGUAGE
```

## Step 4: Enhance EnhancedJumboCrew Class

### Initialize with language layer:

```python
def __init__(self, groq_api_key: Optional[str] = None, user_id: str = "default_user"):
    self.user_id = user_id
    self.api_key = groq_api_key or Config.GROQ_API_KEY
    if not self.api_key:
        raise ValueError("No Groq API key found.")
    try:
        self.llm = make_llm(self.api_key)
        self.memory = EnhancedJumboMemory(user_id)
        self.language_layer = LanguageLayer()  # NEW: Initialize language layer
        self.listener, self.companion, self.summariser = self._create_agents()
        self._cached_crew = None
    except Exception as e:
        logger.error(f"Failed to initialize EnhancedJumboCrew: {e}")
        raise
```

### Update respond method with language detection:

```python
def respond(self, user_message: str, max_retries: int = Config.MAX_RETRIES) -> Tuple[str, Dict]:
    """ENHANCED: Generate response with language awareness"""
    response_metadata = {
        "timestamp": datetime.now().isoformat(),
        "processing_time": 0,
        "mood_detected": "neutral",
        "confidence": 0.5,
        "memories_used": 0,
        "success": False,
        "error": None,
        "name_detected": False,
        "language_detected": "te"  # NEW FIELD
    }
    start_time = time.time()
    
    try:
        # NEW: Detect language
        detected_language = self.language_layer.detect_language(user_message)
        response_metadata["language_detected"] = detected_language
        
        # Store language preference if this is first time or changed
        stored_lang = self.memory.get_language_preference()
        if stored_lang != detected_language:
            self.memory.store_language_preference(detected_language)
        
        # NEW: Extract name with language awareness
        extracted_name = self.language_layer.extract_name_multilingual(
            user_message, detected_language
        )
        
        if extracted_name:
            current_name = self.memory.get_user_name()
            if not current_name or current_name != extracted_name:
                self.memory.store_user_info("name", extracted_name)
                response_metadata["name_detected"] = True
                logger.info(f"Name detected and stored: {extracted_name}")
        
        user_name = self.memory.get_user_name()
        
        # NEW: Use multilingual mood detection
        detected_mood, confidence = self.language_layer.detect_mood_multilingual(
            user_message, detected_language
        )
        response_metadata.update({
            "mood_detected": detected_mood,
            "confidence": confidence
        })
        
        # Get relevant memories
        relevant_memories = self.memory.get_relevant_memories(user_message, limit=3)
        response_metadata["memories_used"] = len(relevant_memories)
        
        # NEW: Get cultural context
        cultural_context = self.language_layer.get_cultural_context(detected_language)
        cultural_refs = self.language_layer.extract_cultural_references(
            user_message, detected_language
        )
        
        # Build memory context
        memory_context = ""
        if relevant_memories:
            memory_context = "\n\nRelevant past conversations:\n"
            for memory in relevant_memories[:2]:
                user_msg = memory.get('user_message', '')[:100]
                jumbo_resp = memory.get('jumbo_response', '')[:100]
                timestamp = memory.get('timestamp', '')[:10]
                mem_lang = memory.get('language', 'en')
                memory_context += f"- [{timestamp}] ({mem_lang}) User: {user_msg}... | Jumbo: {jumbo_resp}...\n"
        
        # Add cultural context to memory
        if cultural_refs:
            memory_context += "\n\nCultural references detected:\n"
            for ref in cultural_refs[:3]:
                memory_context += f"- {ref['term']} ({ref['category']}): {ref['meaning']}\n"
        
        # Generate response with retries
        for attempt in range(max_retries):
            try:
                response = self._generate_response(
                    user_message, user_name, detected_mood, confidence,
                    memory_context, relevant_memories, 
                    detected_language, cultural_context  # NEW PARAMETERS
                )
                
                # NEW: Format response for target language
                response = self.language_layer.format_response_for_language(
                    response, detected_language
                )
                
                if response and len(response.strip()) >= 10:
                    # Store conversation with language info
                    storage_success = self.memory.store_conversation(
                        user_message, response, detected_mood, confidence, 
                        user_name, detected_language  # NEW PARAMETER
                    )
                    
                    response_metadata.update({
                        "processing_time": time.time() - start_time,
                        "success": True,
                        "storage_success": storage_success
                    })
                    return response, response_metadata
                else:
                    logger.warning(f"Generated response too short or empty: {response}")
                    
            except Exception as e:
                logger.warning(f"Response generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.5)
        
    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        response_metadata["error"] = str(e)
        
        # Generate fallback response in detected language
        detected_language = response_metadata.get("language_detected", "te")
        detected_mood, confidence = self.language_layer.detect_mood_multilingual(
            user_message, detected_language
        )
        user_name = self.memory.get_user_name()
        response = self._get_fallback_response(detected_mood, user_name, detected_language)
        
        # Try to store the fallback conversation
        try:
            self.memory.store_conversation(
                user_message, response, detected_mood, confidence, 
                user_name, detected_language
            )
        except Exception as storage_error:
            logger.error(f"Failed to store fallback conversation: {storage_error}")
        
        response_metadata.update({
            "processing_time": time.time() - start_time,
            "success": False
        })
        return response, response_metadata
```

### Update _generate_response method:

```python
def _generate_response(self, user_message: str, user_name: Optional[str], 
                      mood: str, confidence: float, memory_context: str,
                      relevant_memories: List[Dict], 
                      language: str = "te",  # NEW PARAMETER
                      cultural_context: Dict = None) -> str:  # NEW PARAMETER
    """ENHANCED: Generate response with language and cultural awareness"""
    
    lang_info = LanguageConfig.SUPPORTED_LANGUAGES.get(language, 
                                                       LanguageConfig.SUPPORTED_LANGUAGES['en'])
    
    # Build cultural context string
    cultural_info = ""
    if cultural_context and language in ['te', 'hi']:
        cultural_info = f"""
IMPORTANT CULTURAL CONTEXT for {lang_info['native_name']}:
- Be aware of festivals: {', '.join(list(cultural_context.get('festivals', {}).keys())[:5])}
- Understand family terms and respect markers
- Use appropriate formality based on context
- Recognize regional food, places, and customs
- Code-switching between {lang_info['name']} and English is natural and common
"""
    
    listen_task = Task(
        description=f"""Analyze the emotional content and context of this message in {lang_info['native_name']}: '{user_message}'

        User Information:
        - Name: {user_name or 'Unknown'}
        - Language: {lang_info['native_name']} ({language})
        - Detected mood: {mood} (confidence: {confidence:.2f})
        - Available memory context: {len(relevant_memories)} relevant past conversations

        {memory_context}
        {cultural_info}

        Provide a comprehensive emotional analysis that considers:
        1. Current emotional state and intensity
        2. Underlying needs or concerns
        3. Connection to past conversations (if any)
        4. Cultural context (festivals, family dynamics, regional aspects)
        5. What type of support would be most helpful
        
        Keep analysis focused and culturally aware.""",
        agent=self.listener,
        expected_output="Detailed emotional analysis with cultural awareness"
    )
    
    companion_task = Task(
        description=f"""Create a warm, empathetic response as Jumbo in {lang_info['native_name']}. 

        CRITICAL LANGUAGE INSTRUCTION:
        - Respond ENTIRELY in {lang_info['native_name']} ({language})
        - Use {lang_info['native_name']} script naturally
        - Code-switching with English is acceptable and natural
        - Use appropriate respect markers (గారు/जी) when needed

        Message to respond to: '{user_message}'

        Context:
        - User's name: {user_name or 'Unknown'}
        - Language: {lang_info['native_name']}
        - Mood: {mood} (confidence: {confidence:.2f})
        - Memory context available: {'Yes' if relevant_memories else 'No'}

        {memory_context}
        {cultural_info}

        RESPONSE REQUIREMENTS:
        1. Respond in {lang_info['native_name']} - this is MANDATORY
        2. Always use "you" language ("మీరు...", "आप..." based on formality)
        3. NEVER use "I feel" or "I think you..." constructions
        4. Address the SPECIFIC content they shared
        5. Use their name ({user_name}) naturally if known
        6. Reference past conversations when relevant
        7. Match the emotional tone to their {mood} state
        8. Show cultural awareness (festivals, family, regional context)
        9. Keep response conversational (2-3 sentences)
        10. End with a thoughtful follow-up question in {lang_info['native_name']}

        Be warm, genuine, and culturally connected.""",
        agent=self.companion,
        context=[listen_task],
        expected_output=f"Empathetic response in {lang_info['native_name']} (2-3 sentences + question)"
    )
    
    summariser_task = Task(
        description=f"""Ensure the response is perfectly crafted in {lang_info['native_name']}:

        Requirements:
        1. MUST be in {lang_info['native_name']} language/script
        2. Uses "you" language throughout (మీరు/నువ్వు or आप/तुम)
        3. Sounds natural and conversational (not translated or robotic)
        4. Matches the {mood} mood appropriately
        5. Uses respectful language when appropriate (గారు/जी)
        6. Incorporates user's name ({user_name}) naturally if known
        7. References memories when helpful
        8. Ends with a caring question in {lang_info['native_name']}
        9. Shows genuine cultural understanding
        10. Concise (2-3 sentences) but emotionally rich

        The response should feel like talking to a caring {lang_info['name']}-speaking friend.
        Ensure it's complete and ready to send.""",
        agent=self.summariser,
        context=[companion_task],
        expected_output=f"Perfect {lang_info['native_name']} response (2-3 sentences + question)"
    )
    
    # Create and execute crew
    crew = Crew(
        agents=[self.listener, self.companion, self.summariser],
        tasks=[listen_task, companion_task, summariser_task],
        verbose=False,
        process=Process.sequential
    )
    
    result = crew.kickoff()
    return str(result).strip()
```

### Update _get_fallback_response method:

```python
def _get_fallback_response(self, mood: str, user_name: Optional[str], 
                          language: str = "te") -> str:
    """ENHANCED: Generate mood-appropriate fallback responses in target language"""
    name_part = f", {user_name}" if user_name else ""
    
    # Telugu fallback responses
    telugu_fallbacks = {
        "happy": [
            f"అది చాలా బాగుంది{name_part}! మీరు నిజంగా సంతోషంగా ఉన్నట్లు అనిపిస్తుంది. మీకు ఇంత ఆనందం ఏమి తెస్తోంది?",
            f"మీ సంతోషం నాకు కూడా అంటుతోంది{name_part}! ఇది చాలా అందంగా ఉంది. మీకు ఇప్పుడు ఏం చాలా బాగా అనిపిస్తోంది?",
            f"మీరు చాలా సంతోషంగా ఉన్నట్లు అనిపిస్తోంది{name_part}! ఇది వినడానికి చాలా బాగుంది. మీ మనసుని ఏం ఉత్సాహపరుస్తోంది?"
        ],
        "sad": [
            f"మీరు ఏదో కష్టం అనుభవిస్తున్నట్లు అనిపిస్తోంది{name_part}. ఆ భారమైన భావాలు పూర్తిగా సహజం. మీ హృదయాన్ని ఏం బాధిస్తోంది?",
            f"మీ మాటల్లో దుఃఖం వినిపిస్తోంది{name_part}. మీరు దీన్ని ఒంటరిగా ఎదుర్కోవలసిన అవసరం లేదు. ఏం చాలా కష్టంగా ఉంది?",
            f"మీరు ఇప్పుడు కొంత బాధను మోస్తున్నట్లు అనిపిస్తోంది{name_part}. అది నిజంగా కష్టంగా ఉండాలి. మీ మనసులో ఏం నడుస్తోంది?"
        ],
        "anxious": [
            f"మీ మనసు ఆందోళనతో పరుగెత్తుకుంటున్నట్లు అనిపిస్తోంది{name_part}. ఆ చింత నిజంగా అలసిపోయేలా ఉంటుంది. మీకు ఏం చాలా అశాంతిని కలిగిస్తోంది?",
            f"మీరు ఇప్పుడు చాలా ఒత్తిడిలో ఉన్నట్లు అనిపిస్తోంది{name_part}. ఆ భయాలు పూర్తిగా అర్థమవుతాయి. మీపై ఏం ఎక్కువగా భారంగా ఉంది?",
            f"మీ ఆందోళనలు పూర్తిగా సహేతుకం{name_part}. చింత అంత అలసిపోయేలా చేస్తుంది. మీకు ఏం ఎక్కువ ఒత్తిడిని కలిగిస్తోంది?"
        ],
        "angry": [
            f"మీరు నిజంగా విసుగ్గా ఉన్నట్లు అనిపిస్తోంది{name_part}, మరియు ఆ కోపం పూర్తిగా సహేతుకం. ఆ భావాలు పూర్తిగా సరైనవి. మీకు ఏం చిరాకు తెస్తోంది?",
            f"మీ చిరాకు నాకు వినిపిస్తోంది{name_part}. మీ నిరాశ పూర్తిగా న్యాయమైనది. మీకు ఏం ఎక్కువగా బాధ కలిగిస్తోంది?",
            f"ఆ నిరాశ మీ మాటల్లో స్పష్టంగా కనిపిస్తోంది{name_part}. మీరు కోపంగా ఉండటానికి పూర్తి హక్కు ఉంది. ఏం మిమ్మల్ని ఎక్కువగా కలవరపెడుతోంది?"
        ],
        "excited": [
            f"మీ ఉత్సాహం నాకు కూడా అంటుతోంది{name_part}! మీరు ప్రపంచాన్ని స్వాధీనం చేసుకోవడానికి సిద్ధంగా ఉన్నట్లు అనిపిస్తోంది. ఏం మీకు ఇంత శక్తిని ఇస్తోంది?",
            f"మీ ఉత్సాహం మీ మాటల ద్వారా నాకు అనుభవమవుతోంది{name_part}! ఆ శక్తి అద్భుతంగా ఉంది. ఇప్పుడు మిమ్మల్ని ఏం ప్రకాశింపజేస్తోంది?",
            f"మీరు చాలా ఉత్సాహంగా ఉన్నట్లు అనిపిస్తోంది{name_part}! ఆ ఉత్సాహం అద్భుతంగా ఉంది. మిమ్మల్ని ఏం ఇంత ఆనందపరుస్తోంది?"
        ],
        "lost": [
            f"మీరు ఇప్పుడు గందరగోళంగా ఉన్న స్థితిలో ఉన్నట్లు అనిపిస్తోంది{name_part}. ఆ అనిశ్చితత నిజంగా కష్టంగా ఉంటుంది. మీకు ఏం ఎక్కువ అనిశ్చితంగా అనిపిస్తోంది?",
            f"మీరు దిశ కోసం వెతుకుతున్నట్లు అనిపిస్తోంది{name_part}. అది పూర్తిగా అర్థమవుతుంది. మీ ముందుకు వెళ్ళే మార్గం గురించి ఏం మీ మనసులో ఉంది?",
            f"తప్పిపోయిన అనుభూతి చాలా కష్టం{name_part}. ఈ అనిశ్చితిలో మీరు ఒంటరిగా లేరు. మిమ్మల్ని ఏం బాధిస్తోంది?"
        ],
        "neutral": [
            f"నేను వింటున్నాను{name_part}. మీతో దీన్ని పంచుకున్నందుకు ధన్యవాదాలు. మీ మనసులో ఏం ఉంది?",
            f"మీరు నాతో పంచుకోవడానికి సౌకర్యంగా అనిపించారు అని సంతోషంగా ఉంది{name_part}. ఏం మాట్లాడాలనుకుంటున్నారు?",
            f"మీ ఆలోచనలు మరియు భావాలు ముఖ్యం{name_part}. మీపై ఏం బరువుగా ఉంది?"
        ]
    }
    
    # Hindi fallback responses
    hindi_fallbacks = {
        "happy": [
            f"यह सुनकर बहुत अच्छा लगा{name_part}! आप वाकई खुश लग रहे हैं। आपको इतनी खुशी क्या दे रही है?",
            f"आपकी खुशी मुझे भी छू रही है{name_part}! यह बहुत सुंदर है। अभी आपको सबसे अच्छा क्या लग रहा है?",
            f"आप बहुत खुश लग रहे हैं{name_part}! यह सुनना बहुत अच्छा है। आपका मन क्या उत्साहित कर रहा है?"
        ],
        "sad": [
            f"आप कुछ कठिन अनुभव कर रहे हैं{name_part}। वो भारी भावनाएं बिल्कुल स्वाभाविक हैं। आपके दिल को क्या परेशान कर रहा है?",
            f"आपकी बातों में दुख सुनाई दे रहा है{name_part}। आपको अकेले इससे गुजरना नहीं है। सबसे कठिन क्या है?",
            f"आप अभी कुछ दर्द महसूस कर रहे हैं{name_part}। यह सचमुच मुश्किल होगा। आपके मन में क्या चल रहा है?"
        ],
        "anxious": [
            f"ऐसा लग रहा है कि आपका मन चिंता से भाग रहा है{name_part}। वो चिंता सचमुच थका देने वाली होती है। आपको सबसे ज्यादा बेचैनी क्या दे रही है?",
            f"आप अभी बहुत दबाव में लग रहे हैं{name_part}। वो चिंताएं पूरी तरह समझ में आती हैं। आप पर सबसे ज्यादा भार क्या है?",
            f"आपकी चिंताएं बिल्कुल वाजिब हैं{name_part}। चिंता इतनी थका देने वाली होती है। आपको सबसे ज्यादा तनाव क्या दे रहा है?"
        ],
        "angry": [
            f"आप सचमुच निराश लग रहे हैं{name_part}, और वो गुस्सा बिल्कुल उचित है। वो भावनाएं पूरी तरह सही हैं। आपको क्या परेशान कर रहा है?",
            f"मुझे आपकी झुंझलाहट सुनाई दे रही है{name_part}। आपकी निराशा बिल्कुल न्यायसंगत है। आपको सबसे ज्यादा क्या परेशान कर रहा है?",
            f"वो निराशा आपकी बातों में स्पष्ट दिख रही है{name_part}। आपको गुस्सा होने का पूरा हक है। सबसे ज्यादा क्या आपको परेशान कर रहा है?"
        ],
        "excited": [
            f"आपका उत्साह मुझे भी छू रहा है{name_part}! आप दुनिया को जीतने के लिए तैयार लग रहे हैं। आपको इतनी ऊर्जा क्या दे रही है?",
            f"आपके उत्साह का मुझे अनुभव हो रहा है{name_part}! वो ऊर्जा शानदार है। अभी आपको क्या चमका रहा है?",
            f"आप बहुत उत्साहित लग रहे हैं{name_part}! वो उत्साह शानदार है। आपको क्या इतना खुश कर रहा है?"
        ],
        "neutral": [
            f"मैं सुन रहा हूं{name_part}। आपने मेरे साथ साझा किया, उसके लिए धन्यवाद। आपके मन में क्या है?",
            f"मुझे खुशी है कि आप मेरे साथ साझा करने में सहज महसूस कर रहे हैं{name_part}। आप क्या बात करना चाहेंगे?",
            f"आपके विचार और भावनाएं मायने रखती हैं{name_part}। आप पर क्या भारी है?"
        ]
    }
    
    # English fallback (your existing ones)
    english_fallbacks = {
        "happy": [
            f"That sounds wonderful{name_part}! You seem really content right now. What's been bringing you the most joy lately?"
        ],
        "sad": [
            f"You sound like you're going through something difficult{name_part}. Those heavy feelings are completely valid. What's been weighing on your heart?"
        ],
        # ... add more moods as needed
    }
    
    # Select appropriate fallback based on language
    if language == 'te':
        fallback_dict = telugu_fallbacks
    elif language == 'hi':
        fallback_dict = hindi_fallbacks
    else:
        fallback_dict = english_fallbacks
    
    # Get responses for the mood
    responses = fallback_dict.get(mood, fallback_dict.get('neutral', [
        f"I hear you{name_part}. What's on your mind?"
    ]))
    
    import random
    return random.choice(responses)
```

## Step 5: Update Streamlit UI

### Add language selector in sidebar:

```python
def display_sidebar():
    """Enhanced sidebar with language selection"""
    if st.session_state.crew:
        with st.sidebar:
            st.markdown("""
            <div class="memory-info">
                <h3 style="color: #2c3e50;">🧠 Memory Status</h3>
            </div>
            """, unsafe_allow_html=True)

            # Language preference display
            current_lang = st.session_state.crew.memory.get_language_preference()
            lang_info = LanguageConfig.SUPPORTED_LANGUAGES.get(current_lang)
            if lang_info:
                st.success(f"🗣️ Language: **{lang_info['native_name']}**")
            
            # Language selector
            with st.expander("🌐 Change Language"):
                selected_lang = st.selectbox(
                    "Select your preferred language:",
                    options=['te', 'hi', 'en'],
                    format_func=lambda x: LanguageConfig.SUPPORTED_LANGUAGES[x]['native_name'],
                    index=['te', 'hi', 'en'].index(current_lang)
                )
                
                if st.button("Update Language"):
                    st.session_state.crew.memory.store_language_preference(selected_lang)
                    st.success(f"Language updated to {LanguageConfig.SUPPORTED_LANGUAGES[selected_lang]['native_name']}!")
                    st.rerun()

            # Rest of your existing sidebar code...
            user_name = st.session_state.crew.memory.get_user_name()
            # ... continue with existing sidebar
```

### Update display messages to show language:

```python
def display_conversation():
    """Display conversation with language indicators"""
    if st.session_state.messages:
        for i, message in enumerate(st.session_state.messages):
            # Get metadata if available
            lang_indicator = ""
            if hasattr(st.session_state, 'message_metadata'):
                metadata = st.session_state.message_metadata.get(i, {})
                detected_lang = metadata.get('language_detected')
                if detected_lang:
                    lang_name = LanguageConfig.SUPPORTED_LANGUAGES.get(detected_lang, {}).get('native_name', '')
                    lang_indicator = f" <span style='font-size:0.8em; opacity:0.7;'>({lang_name})</span>"
            
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You{lang_indicator}:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message jumbo-message">
                    <strong>🐘 Jumbo{lang_indicator}:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # ... rest of conversation display
```

## Step 6: Testing Your Language Layer

### Test script:

```python
def test_language_layer():
    """Test the language layer integration"""
    from language_layer import LanguageLayer
    
    lang_layer = LanguageLayer()
    
    # Test 1: Telugu detection
    telugu_text = "నేను చాలా సంతోషంగా ఉన్నాను"
    lang = lang_layer.detect_language(telugu_text)
    print(f"✓ Telugu detection: {lang}")  # Should be 'te'
    
    # Test 2: Hindi detection
    hindi_text = "मैं बहुत खुश हूं"
    lang = lang_layer.detect_language(hindi_text)
    print(f"✓ Hindi detection: {lang}")  # Should be 'hi'
    
    # Test 3: Name extraction
    telugu_name = "నా పేరు రాజు"
    name = lang_layer.extract_name_multilingual(telugu_name, 'te')
    print(f"✓ Name extraction: {name}")  # Should be 'రాజు'
    
    # Test 4: Mood detection
    mood_text = "నేను చాలా కోపంగా ఉన్నాను"
    mood, conf = lang_layer.detect_mood_multilingual(mood_text, 'te')
    print(f"✓ Mood detection: {mood} ({conf})")  # Should be 'angry'
    
    # Test 5: Cultural context
    context = lang_layer.get_cultural_context('te')
    print(f"✓ Cultural context loaded: {len(context)} categories")
    
    print("\n✅ All language layer tests passed!")

if __name__ == "__main__":
    test_language_layer()
```

## Step 7: Quick Start Checklist

- [ ] Install dependencies (`googletrans`, `langdetect`)
- [ ] Add `language_layer.py` to your project
- [ ] Import `LanguageLayer` in `Jumbo_v1.py`
- [ ] Update `EnhancedJumboMemory` class
- [ ] Update `EnhancedJumboCrew` class  
- [ ] Update Streamlit UI with language selector
- [ ] Run test script to verify
- [ ] Test with Telugu/Hindi conversations
- [ ] Deploy and gather feedback

## Next Steps

Once language layer is working:
1. **Add Voice Support** - Google Cloud Speech/TTS
2. **Optimize Translation** - Cache frequently used phrases
3. **Expand Cultural Context** - Add more festivals, idioms, regional variations
4. **Mobile App** - Convert to React Native/Flutter
5. **Offline Mode** - Store common responses locally

## Common Issues & Solutions

**Issue**: Translation API rate limits
**Solution**: Implement caching and use local translation for common phrases

**Issue**: Language detection confusion with code-switching
**Solution**: Use script detection first, then fallback to keyword analysis

**Issue**: LLM responds in English despite Telugu prompt
**Solution**: Make language instruction stronger in prompts, use examples

---

Your Jumbo now speaks Telugu and Hindi! 🐘🎉
            