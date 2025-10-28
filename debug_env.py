#!/usr/bin/env python3
"""
Debug Environment Variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Environment Variables Debug")
print("=" * 40)

# Check Supabase variables
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_ANON_KEY: {supabase_key[:20]}..." if supabase_key else "SUPABASE_ANON_KEY: None")
print(f"SUPABASE_SERVICE_ROLE_KEY: {supabase_service_key[:20]}..." if supabase_service_key else "SUPABASE_SERVICE_ROLE_KEY: None")

# Check if URL is valid
if supabase_url:
    print(f"\nURL Length: {len(supabase_url)}")
    print(f"URL starts with https: {supabase_url.startswith('https://')}")
    print(f"URL contains supabase.co: {'supabase.co' in supabase_url}")
else:
    print("\n❌ SUPABASE_URL is None or empty")

# Test Supabase connection
try:
    from supabase import create_client
    if supabase_url and supabase_key:
        client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
    else:
        print("❌ Missing URL or key")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")