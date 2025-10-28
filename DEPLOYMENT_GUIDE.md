# 🚀 Jumbo Deployment Guide

## Overview
This guide covers deploying Jumbo's emotional AI chatbot to production using:
- **Frontend**: Vercel (React app)
- **Backend**: Render (Flask API)
- **Database**: Supabase (PostgreSQL)

## 📋 Prerequisites

### Required Accounts
1. **Vercel Account** - [vercel.com](https://vercel.com)
2. **Render Account** - [render.com](https://render.com)
3. **Supabase Account** - [supabase.com](https://supabase.com)
4. **Groq Account** - [console.groq.com](https://console.groq.com)
5. **GitHub Account** - For code repository

### Required API Keys
- Groq API Key (for LLM)
- Supabase URL and Anon Key
- Google OAuth credentials (optional)

## 🤖 LLM Setup (Groq)

### 1. Create Groq Account
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Generate an API key from the dashboard
4. Note: Groq offers free tier with generous limits

### 2. Available Models
Your system is configured to use:
- **Default Model**: `llama3-8b-8192`
- **Alternative Models**: `mixtral-8x7b-32768`, `gemma-7b-it`
- **Configuration**: Set via `LLM_MODEL` environment variable

## 🗄️ Database Setup (Supabase)

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note your project URL and anon key

### 2. Run Database Migrations
Execute these SQL files in Supabase SQL Editor:
```sql
-- Run in order:
1. supabase_schema.sql
2. supabase_onboarding_migration.sql
3. supabase_complete_schema.sql
```

### 3. Configure Authentication
1. Go to Authentication > Settings
2. Enable Google OAuth (optional)
3. Add your domain to allowed origins

## 🖥️ Backend Deployment (Render)

### 1. Connect Repository
1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Select "Web Service"

### 2. Configure Environment Variables
Set these in Render dashboard:
```
FLASK_ENV=production
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_api_key
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

### 3. Deploy Settings
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
- **Health Check Path**: `/health`

## 🌐 Frontend Deployment (Vercel)

### 1. Connect Repository
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Select the `jumbo-ui` folder as root

### 2. Configure Environment Variables
Set these in Vercel dashboard:
```
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
REACT_APP_API_URL=https://your-render-app.onrender.com
```

### 3. Build Settings
- **Framework Preset**: Create React App
- **Build Command**: `npm run build`
- **Output Directory**: `build`

## 🔧 Post-Deployment Configuration

### 1. Update CORS Origins
Update your Render backend environment variable:
```
CORS_ORIGINS=https://your-actual-vercel-domain.vercel.app
```

### 2. Test the Application
1. Visit your Vercel URL
2. Test Google OAuth login
3. Complete onboarding flow
4. Test chat functionality
5. Test profile page

### 3. Configure Custom Domain (Optional)
- Add custom domain in Vercel
- Update CORS_ORIGINS accordingly

## 🚨 Troubleshooting

### Common Issues

**CORS Errors**
- Ensure CORS_ORIGINS matches your Vercel domain exactly
- Check both HTTP and HTTPS variants

**Authentication Issues**
- Verify Supabase OAuth settings
- Check redirect URLs in Google OAuth console

**API Connection Issues**
- Verify REACT_APP_API_URL points to Render backend
- Check Render service is running and healthy

**Database Issues**
- Ensure all SQL migrations ran successfully
- Check Supabase connection from Render logs

### Health Checks
- Backend health: `https://your-render-app.onrender.com/health`
- Frontend: Should load without errors

## 📊 Monitoring

### Render Monitoring
- Check service logs for errors
- Monitor response times
- Set up alerts for downtime

### Vercel Monitoring
- Check function logs
- Monitor build times
- Review analytics

### Supabase Monitoring
- Monitor database performance
- Check authentication metrics
- Review API usage

## 🔒 Security Checklist

- [ ] Environment variables are secure
- [ ] CORS is properly configured
- [ ] Supabase RLS policies are enabled
- [ ] API keys are not exposed in frontend
- [ ] HTTPS is enforced
- [ ] Authentication is working properly

## 🎯 Production URLs

After deployment, you'll have:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-api.onrender.com`
- **Database**: Supabase hosted

Your Jumbo emotional AI chatbot is now live! 🌟