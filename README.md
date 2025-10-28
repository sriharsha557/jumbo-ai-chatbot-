# 🤖 Jumbo - Emotional AI Chatbot

> An intelligent, empathetic AI companion that understands and responds to your emotions.

![Jumbo Demo](https://via.placeholder.com/800x400/0ea5e9/ffffff?text=Jumbo+AI+Chatbot)

## ✨ Features

### 🧠 **Emotional Intelligence**
- **Emotion Detection** - Analyzes text to understand your mood
- **Adaptive Responses** - Tailors conversations based on emotional context
- **Memory System** - Remembers past conversations and preferences
- **Personality Matching** - Adjusts communication style to your preferences

### 🎨 **Beautiful Interface**
- **Glassmorphism Design** - Modern, elegant UI with gradient backgrounds
- **Responsive Layout** - Works perfectly on desktop and mobile
- **Smooth Animations** - Delightful micro-interactions
- **Dark/Light Themes** - Comfortable viewing in any environment

### 🔐 **Secure & Personal**
- **Google OAuth** - Secure authentication via Supabase
- **Privacy First** - Your conversations are private and secure
- **Profile Management** - Customize your AI interaction preferences
- **Data Control** - Full control over your personal data

## 🚀 **Live Demo**

- **Frontend**: [https://your-app.vercel.app](https://your-app.vercel.app)
- **API**: [https://your-api.onrender.com](https://your-api.onrender.com)

## 🛠️ **Tech Stack**

### **Frontend**
- **React.js** - Modern UI framework
- **Supabase Auth** - Authentication and user management
- **Lucide Icons** - Beautiful, consistent iconography
- **CSS3** - Custom styling with glassmorphism effects

### **Backend**
- **Flask** - Python web framework
- **Supabase** - PostgreSQL database and authentication
- **Groq API** - Fast LLM inference with Llama3
- **Gunicorn** - Production WSGI server

### **AI & ML**
- **Groq Llama3-8b** - Large language model for conversations
- **Emotion Detection** - Text-based sentiment analysis
- **Memory System** - Conversation context and user preferences
- **Personality Engine** - Adaptive response generation

## 📋 **Quick Start**

### **Prerequisites**
- Node.js 16+ and npm
- Python 3.8+
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Supabase account (free at [supabase.com](https://supabase.com))

### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/jumbo-ai-chatbot.git
cd jumbo-ai-chatbot
```

### **2. Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run Flask server
python app.py
```

### **3. Frontend Setup**
```bash
# Navigate to frontend
cd jumbo-ui

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your keys

# Start development server
npm start
```

### **4. Database Setup**
1. Create Supabase project
2. Run SQL migrations in order:
   - `supabase_schema.sql`
   - `supabase_onboarding_migration.sql`
   - `supabase_complete_schema.sql`

## 🌐 **Deployment**

### **Free Tier Deployment**
- **Frontend**: Deploy to Vercel (free)
- **Backend**: Deploy to Render (free tier)
- **Database**: Supabase (free tier)
- **LLM**: Groq (generous free tier)

**Total Cost**: $0 for moderate usage!

### **Deployment Guides**
- 📖 [Complete Deployment Guide](DEPLOYMENT_GUIDE.md)
- ✅ [Production Checklist](PRODUCTION_CHECKLIST.md)
- 🚀 [Deployment Ready Summary](DEPLOYMENT_READY.md)

## 🎯 **User Journey**

1. **Landing Page** → Beautiful introduction with gradient background
2. **Google Login** → Secure OAuth authentication
3. **Onboarding** → 7-step preference collection
4. **Chat Interface** → Intelligent, emotional conversations
5. **Profile Management** → Update preferences anytime

## 🔧 **Configuration**

### **Environment Variables**

**Backend (.env)**
```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
CORS_ORIGINS=http://localhost:3000
```

**Frontend (jumbo-ui/.env.local)**
```env
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
REACT_APP_API_URL=http://localhost:5000
```

## 📁 **Project Structure**

```
jumbo-ai-chatbot/
├── jumbo-ui/                 # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── lib/             # Supabase client
│   │   └── theme/           # Design system
│   ├── public/              # Static assets
│   └── package.json
├── api/                     # Flask API routes
├── services/                # Business logic
├── database/                # Database utilities
├── personality/             # AI personality system
├── app.py                   # Flask application
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
└── README.md
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Groq** - For blazing fast LLM inference
- **Supabase** - For excellent backend-as-a-service
- **React** - For the amazing frontend framework
- **Vercel & Render** - For free hosting solutions

## 📞 **Support**

- 📧 **Email**: support@jumbo-ai.com
- 💬 **Discord**: [Join our community](https://discord.gg/jumbo-ai)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/jumbo-ai-chatbot/issues)

---

**Made with ❤️ by the Jumbo Team**

*Bringing emotional intelligence to AI conversations, one chat at a time.*