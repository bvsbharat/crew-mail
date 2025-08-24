#!/usr/bin/env python3
"""
Simple test script for the User Details Crew.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

from user_details_crew import UserDetailsCrew

def test_crew():
    """Test the User Details Crew with a simple example."""
    print("🔍 Testing User Details Crew...")
    
    try:
        # Initialize the crew
        crew = UserDetailsCrew()
        print("✅ Crew initialized successfully")
        
        # Test with a known email
        email = "marco@vapi.ai"
        name = "Marco Bariani"
        
        print(f"📧 Testing with email: {email}")
        print(f"👤 Name: {name}")
        
        # Fetch user details
        user_details = crew.fetch_user_details(
            email=email,
            name=name,
            force_refresh=False
        )
        
        print("\n✅ User details fetched successfully!")
        print(f"📧 Email: {user_details.email}")
        print(f"👤 Name: {user_details.name}")
        print(f"🏢 Company: {user_details.company}")
        print(f"💼 Role: {user_details.role}")
        print(f"📍 Location: {user_details.location}")
        
        if user_details.bio:
            print(f"📝 Bio: {user_details.bio[:100]}...")
        
        print(f"🔗 LinkedIn: {user_details.linkedin_url or 'Not found'}")
        print(f"🐦 Twitter: {user_details.twitter_url or 'Not found'}")
        print(f"🌐 Website: {user_details.website or 'Not found'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crew()
    sys.exit(0 if success else 1)