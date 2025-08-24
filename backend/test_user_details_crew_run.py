#!/usr/bin/env python3
"""
Test script to run the User Details Crew
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from email_auto_responder_flow.crews.user_details_crew.user_details_crew import UserDetailsCrew
from email_auto_responder_flow.models import UserDetails

def test_user_details_crew():
    """
    Test the User Details Crew with sample data
    """
    print("🚀 Starting User Details Crew Test...")
    print("=" * 50)
    
    # Initialize the crew
    try:
        crew = UserDetailsCrew()
        print("✅ User Details Crew initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize crew: {e}")
        return
    
    # Test data - you can modify these
    test_email = "marco@vapi.ai"
    test_name = "Marco"
    
    print(f"\n🔍 Researching user details for:")
    print(f"   Email: {test_email}")
    print(f"   Name: {test_name}")
    print("\n⏳ This may take a few minutes...")
    
    try:
        # Fetch user details using the crew
        user_details = crew.fetch_user_details(
            email=test_email,
            name=test_name,
            force_refresh=True  # Set to True to always fetch fresh data
        )
        
        print("\n✅ User details research completed!")
        print("=" * 50)
        print("📊 Results:")
        print(f"   Email: {user_details.email}")
        print(f"   Name: {user_details.name}")
        print(f"   Company: {user_details.company}")
        print(f"   Role: {user_details.role}")
        print(f"   Bio: {user_details.bio}")
        print(f"   LinkedIn: {user_details.linkedin_url}")
        print(f"   Twitter: {user_details.twitter_url}")
        print(f"   Website: {user_details.website}")
        print(f"   Location: {user_details.location}")
        print(f"   Industry: {user_details.industry}")
        print(f"   Source: {user_details.source}")
        print(f"   Created: {user_details.created_at}")
        print(f"   Updated: {user_details.updated_at}")
        
    except Exception as e:
        print(f"\n❌ Error during user details research: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    Main function to run the test
    """
    # Check for required environment variables
    required_env_vars = [
        "OPENAI_API_KEY",
        "EXA_API_KEY",
        "SERPER_API_KEY",
        "SONAR_API_KEY"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or environment.")
        return
    
    print("✅ All required environment variables are set")
    
    # Run the test
    test_user_details_crew()

if __name__ == "__main__":
    main()