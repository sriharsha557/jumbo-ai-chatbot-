#!/bin/bash
# Deploy to free tier (Render free, Vercel free)

echo "🚀 Deploying to FREE TIER"
echo "Using minimal ML capabilities"

# Set deployment tier
export DEPLOYMENT_TIER=free

# Use minimal requirements
cp requirements.txt requirements-deploy.txt

# Deploy to Render (free tier)
echo "📦 Deploying backend to Render..."
# Render will automatically deploy from GitHub

# Deploy to Vercel (free tier) 
echo "🌐 Deploying frontend to Vercel..."
# Vercel will automatically deploy from GitHub

echo "✅ Free tier deployment initiated"
echo "💡 Limitations: Keyword-based emotion detection, 512MB RAM"