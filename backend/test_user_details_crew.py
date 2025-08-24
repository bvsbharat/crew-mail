#!/usr/bin/env python
"""
Test script to run the User Details Crew directly.

This script demonstrates how to use the UserDetailsCrew to fetch user details
for a given email address and name.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from email_auto_responder_flow.crews.user_details_crew.user_details_crew import UserDetailsCrew

def test_user_details_crew():
    """
    Test the UserDetailsCrew with a sample email and name.
    """
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY", "EXA_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please add these to your .env file:")
        for var in missing_vars:
            print(f"  {var}=your_{var.lower()}_here")
        return False
    
    print("✅ Environment variables found")
    print("🚀 Initializing UserDetailsCrew...")
    
    try:
        # Initialize the crew
        crew = UserDetailsCrew()
        print("✅ UserDetailsCrew initialized successfully")
        
        # Test with sample data
        test_email = "test@example.com"
        test_name = "John Doe"
        
        print(f"\n🔍 Fetching user details for:")
        print(f"  Email: {test_email}")
        print(f"  Name: {test_name}")
        print("\n⏳ This may take a few moments...")
        
        # Fetch user details
        user_details = crew.fetch_user_details(
            email=test_email,
            name=test_name,
            force_refresh=True
        )
        
        print("\n✅ User details fetched successfully!")
        print("\n📋 Results:")
        print(f"  Email: {user_details.email}")
        print(f"  Name: {user_details.name}")
        print(f"  Company: {user_details.company}")
        print(f"  Role: {user_details.role}")
        print(f"  Bio: {user_details.bio}")
        print(f"  LinkedIn: {user_details.linkedin_url}")
        print(f"  Twitter: {user_details.twitter_url}")
        print(f"  Website: {user_details.website}")
        print(f"  Location: {user_details.location}")
        print(f"  Industry: {user_details.industry}")
        print(f"  Source: {user_details.source}")
        print(f"  Created: {user_details.created_at}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running UserDetailsCrew: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Main function to run the test.
    """
    print("🎯 User Details Crew Test")
    print("=" * 50)
    
    success = test_user_details_crew()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("\n💡 To use the crew in your code:")
        print("")
        print("from email_auto_responder_flow.crews.user_details_crew.user_details_crew import UserDetailsCrew")
        print("")
        print("crew = UserDetailsCrew()")
        print("user_details = crew.fetch_user_details('email@example.com', 'Name')")
    else:
        print("\n❌ Test failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)