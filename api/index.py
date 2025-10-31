"""
Vercel serverless function entry point for Flask app
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create the Flask app
app = create_app()

# Vercel expects the app to be available as 'app'
# This will handle all requests to /api/*
def handler(request):
    return app(request.environ, lambda status, headers: None)

# For Vercel
if __name__ == "__main__":
    app.run()