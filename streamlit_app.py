"""
streamlit_app.py - Modular Streamlit UI with Login/Register
"""

import streamlit as st
from chatbot import JumboChatbot
from language_utils import Language
import sys

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Jumbo Chatbot",
    page_icon="🐘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling - UPDATED for centered layout
st.markdown("""
<style>
    /* Center main content */
    .main {
        max-width: 900px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    .user-message {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        margin-left: 1rem;
    }
    .bot-message {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        margin-right: 1rem;
    }
    .info-box {
        background-color: #c8e6c9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .error-box {
        background-color: #ffcdd2;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #c8e6c9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = JumboChatbot()

if 'user_registered' not in st.session_state:
    st.session_state.user_registered = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "login"  # "login" or "register"

chatbot = st.session_state.chatbot

# ============================================================================
# SIDEBAR - LOGIN / REGISTER
# ============================================================================

def display_auth_sidebar():
    """Display login/register interface"""
    with st.sidebar:
        # Display sidebar image - SMALL SIZE (120px)
        try:
            col = st.columns([1])[0]
            with col:
                st.image("assets/newjumbo.png", width=120)
        except:
            pass
        
        st.markdown("## 🐘 Jumbo Chatbot")
        
        # Toggle between Login and Register
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔑 Login", use_container_width=True, 
                        key="login_btn",
                        type="primary" if st.session_state.auth_mode == "login" else "secondary"):
                st.session_state.auth_mode = "login"
                st.rerun()
        
        with col2:
            if st.button("✍️ Register", use_container_width=True,
                        key="register_btn",
                        type="primary" if st.session_state.auth_mode == "register" else "secondary"):
                st.session_state.auth_mode = "register"
                st.rerun()
        
        st.divider()
        
        # LOGIN MODE
        if st.session_state.auth_mode == "login":
            st.markdown("### 🔓 Login")
            st.write("Enter your name to continue chatting.")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                login_name = st.text_input(
                    "Your name:",
                    placeholder="Enter your name",
                    key="login_name_input"
                )
            
            with col2:
                if st.button("Login", key="login_submit_btn", use_container_width=True):
                    if not login_name or len(login_name) < 2:
                        st.error("Name must be at least 2 characters long.")
                    else:
                        # Check if user exists
                        if not chatbot.user_exists(login_name):
                            st.error(f"❌ User '{login_name}' not found. Please register first.")
                        else:
                            # Login user
                            chatbot.set_current_user(login_name, "te")
                            st.session_state.user_registered = True
                            st.session_state.current_user = login_name
                            st.success(f"✅ Welcome back, {login_name}!")
                            st.rerun()
        
        # REGISTER MODE
        else:
            st.markdown("### ✏️ Register New Account")
            st.write("Create a new account to start chatting.")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                register_name = st.text_input(
                    "Choose a name:",
                    placeholder="Your unique name",
                    key="register_name_input"
                )
            
            with col2:
                if st.button("Register", key="register_submit_btn", use_container_width=True):
                    if not register_name or len(register_name) < 2:
                        st.error("Name must be at least 2 characters long.")
                    else:
                        # Check if name already exists
                        if chatbot.user_exists(register_name):
                            st.error(f"❌ '{register_name}' is already taken. Please choose a different name.")
                        else:
                            # Register new user
                            success, message = chatbot.register_new_user(register_name, "te")
                            if success:
                                st.session_state.user_registered = True
                                st.session_state.current_user = register_name
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")

def display_chat_sidebar():
    """Display sidebar when user is logged in"""
    with st.sidebar:
        # Display sidebar image - smaller size
        try:
            st.image("assets/newjumbo.png", use_container_width=True)
        except:
            pass
        
        # User is registered
        user_info = chatbot.get_current_user()
        if user_info:
            st.markdown(f"### Welcome, {user_info.get('name')}!")
            
            # Display language
            current_lang = Language(user_info.get("language")).value
            st.info(f"🗣️ Language: **{Language(current_lang).name}**")
            
            # User stats
            stats = chatbot.get_user_stats()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Conversations", stats.get("total_conversations", 0))
            with col2:
                st.metric("Member since", stats.get("created_at", "")[:10])
            
            st.divider()
            
            # View conversation summary
            if st.button("📋 View Summary", use_container_width=True):
                summary = chatbot.get_conversation_summary()
                if summary:
                    st.info(summary)
            
            # Logout
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user_registered = False
                st.session_state.current_user = None
                st.session_state.messages = []
                st.session_state.auth_mode = "login"
                st.rerun()

# ============================================================================
# MAIN CHAT AREA
# ============================================================================

if not st.session_state.user_registered:
    # Show auth sidebar
    display_auth_sidebar()
    
    # Show welcome page
    st.markdown("# 🐘 Jumbo Chatbot")
    
    # Display main GIF - CENTERED, MEDIUM SIZE (300px) - ANIMATED
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.markdown(
                f'<div style="text-align: center;"><img src="assets/newjumbo.gif" width="300" alt="Jumbo"></div>',
                unsafe_allow_html=True
            )
        except:
            st.write("Loading Jumbo...")
    
    st.markdown("## Welcome to Jumbo - Your Personal Telugu/Hindi AI Companion")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### ✨ Features
        - Native Telugu support
        - Native Hindi support
        - Conversation memory
        - Personalized responses
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 How It Works
        1. Register with unique name
        2. Chat in your language
        3. Jumbo remembers everything
        4. Get personalized support
        """)
    
    with col3:
        st.markdown("""
        ### 🌍 Languages
        - తెలుగు (Telugu)
        - हिंदी (Hindi)
        - English
        """)
    
    st.divider()
    st.markdown("👈 **Login or Register in the sidebar to get started!**")

else:
    # Show chat sidebar
    display_chat_sidebar()
    
    # User is logged in - show chat interface
    # Display small Jumbo image at top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("assets/newjumbo.png", use_container_width=True)
        except:
            pass
    
    
    # Display small Jumbo image at top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("assets/newjumbo.png", use_container_width=True)
        except:
            pass
    
    st.markdown(f"# 🐘 Chat with Jumbo")
    st.markdown(f"_Chatting as **{st.session_state.current_user}**_")
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <b>You:</b> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bot-message">
                    <b>😊 Jumbo:</b> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Input area - MUST be outside columns/sidebar
    user_input = st.chat_input(
        "Type your message in Telugu, Hindi, or English...",
        key="chat_input"
    )
    
    # Process user input
    if user_input:
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Get chatbot response
        with st.spinner("Jumbo is thinking..."):
            try:
                response, metadata = chatbot.process_message(user_input)
                
                # Add bot response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
                # Display metadata in sidebar
                with st.sidebar:
                    st.markdown("### 📊 Last Response")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Mood", metadata.get("mood", "neutral"))
                    with col2:
                        confidence = metadata.get("mood_confidence", 0)
                        st.metric("Confidence", f"{confidence:.0%}")
                    
                    if metadata.get("response_type"):
                        st.caption(f"Type: {metadata.get('response_type')}")
                    
                    if metadata.get("used_llm"):
                        st.caption("🤖 LLM Response")
                    
                    st.caption(f"Language: {metadata.get('detected_language')}")
                
                st.rerun()
            
            except Exception as e:
                st.error(f"Error processing message: {str(e)}")
                st.session_state.messages.pop()  # Remove failed message

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**Jumbo Chatbot v2.0** | Modular Architecture | Multi-language Support
Built with ❤️ for Telugu and Hindi communities
""")