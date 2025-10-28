# Supabase Integration Setup Guide

## 🚀 Quick Setup

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up/login and click **New Project**
3. Choose your organization and enter:
   - **Name**: `jumbo-chatbot`
   - **Database Password**: (create a strong password)
   - **Region**: Choose closest to you
4. Click **Create new project** and wait for setup (2-3 minutes)

### 2. Set Up Google OAuth
1. In your Supabase dashboard, go to **Authentication** → **Providers**
2. Find **Google** and click to configure
3. **Enable Google provider**
4. You'll need Google OAuth credentials:

#### Get Google OAuth Credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Go to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client IDs**
5. Choose **Web application**
6. Add these **Authorized redirect URIs**:
   ```
   https://your-project-id.supabase.co/auth/v1/callback
   http://localhost:3000
   ```
7. Copy the **Client ID** and **Client Secret**

#### Configure in Supabase:
1. Back in Supabase **Authentication** → **Providers** → **Google**
2. Paste your **Client ID** and **Client Secret**
3. Click **Save**

### 3. Run Database Schema
1. Go to your Supabase dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `supabase_schema.sql`
4. Click **Run** to create all tables, policies, and triggers

### 4. Get Your Credentials
1. Go to **Settings** → **API**
2. Copy your:
   - **Project URL** (looks like: `https://abc123.supabase.co`)
   - **Anon public key** (starts with `eyJ...`)
   - **Service role key** (starts with `eyJ...` - keep this secret!)

### 5. Update Environment Variables
Update your `.env` file with your actual Supabase credentials:

```env
# Supabase Configuration (Backend)
SUPABASE_URL=https://your-actual-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# React App Configuration (Frontend)
REACT_APP_SUPABASE_URL=https://your-actual-project-id.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Important**: Replace the example values with your actual credentials from step 4!

### 6. Install Dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend (if not already done)
cd jumbo-ui
npm install
```

### 7. Update Frontend for Supabase
Update your React components to use Supabase authentication:

1. **Uncomment Supabase imports** in:
   - `jumbo-ui/src/components/AuthPage.jsx`
   - `jumbo-ui/src/components/ChatPage.jsx`

2. **Update AuthPage** to use Google login (I'll create this for you)

### 8. Run the Application

**Stop the old API first**, then run:

**Backend (with Supabase):**
```bash
python flask_api_supabase.py
```

**Frontend:**
```bash
cd jumbo-ui
npm start
```

### 9. Test the Setup
1. Go to `http://localhost:3000`
2. You should see **"Sign in with Google"** button
3. Click it to authenticate via Google
4. Start chatting with Jumbo!

## 📊 Database Schema Overview

### Tables Created:
- **profiles** - User profiles linked to Supabase Auth
- **conversations** - Chat history with mood tracking
- **user_memories** - User relationships, preferences, and context
- **mood_history** - Mood tracking for emotional patterns

### Features Enabled:
- ✅ Row Level Security (RLS) - Users can only access their own data
- ✅ Automatic profile creation on signup
- ✅ Real-time subscriptions ready
- ✅ Mood and conversation tracking
- ✅ Memory system for personalization

## 🔄 Migration from Local Storage

If you have existing users, you can migrate them by:

1. **Export existing data** from your current system
2. **Use the admin functions** in `supabase_service.py`
3. **Bulk insert** using Supabase's batch operations

## 🛡️ Security Features

- **Authentication** handled by Supabase Auth
- **Row Level Security** ensures data isolation
- **API keys** with different permission levels
- **Automatic user profile** creation
- **Session management** built-in

## 📱 Frontend Integration

The React app now includes:
- Supabase client setup (`src/lib/supabase.js`)
- Authentication helpers
- Database operation helpers
- Real-time subscription ready

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/signup` - Sign up new user
- `POST /api/auth/signin` - Sign in user  
- `POST /api/auth/signout` - Sign out user
- `GET /api/auth/user` - Get current user

### Chat & Data
- `POST /api/chat/message` - Send message (saves to Supabase)
- `GET /api/chat/history` - Get conversation history
- `GET /api/memories` - Get user memories
- `POST /api/memories` - Save user memory
- `GET /api/mood/history` - Get mood tracking data
- `GET /api/stats` - Get user statistics

## 🎯 Next Steps

1. **Test the setup** with the new API endpoints
2. **Update your React components** to use Supabase auth
3. **Enable real-time features** if needed
4. **Set up email templates** in Supabase for auth flows
5. **Configure storage** if you need file uploads

## 🔄 Switch to Supabase Authentication

Once you've completed the setup above, update your React app:

1. **Replace AuthPage import** in `jumbo-ui/src/App.js`:
```javascript
// Change this line:
import AuthPage from './components/AuthPage';

// To this:
import AuthPage from './components/AuthPageSupabase';
```

2. **Uncomment Supabase imports** in your components (already prepared)

3. **Restart your applications**:
```bash
# Stop current Flask API (Ctrl+C)
# Start Supabase API
python flask_api_supabase.py

# In another terminal
cd jumbo-ui
npm start
```

## 🆘 Troubleshooting

**Common Issues:**

1. **"Registration failed"** - You're still using the old API
   - Make sure you're running `flask_api_supabase.py` not `flask_api.py`
   - Check environment variables are set

2. **Google login not working**
   - Verify redirect URIs in Google Console
   - Check Supabase Google provider is enabled
   - Ensure your domain is added to Supabase allowed origins

3. **Environment variables not found**
   - Make sure `.env` file has actual values, not placeholders
   - Restart both backend and frontend after updating `.env`

**Test Connection:**
```bash
# Test Supabase backend
curl http://localhost:5000/api/health

# Should return: {"supabase_initialized": true}
```

**Quick Debug:**
- Check browser console for errors
- Verify Supabase project is active (not paused)
- Test Google OAuth in Supabase Auth logs