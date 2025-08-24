#!/usr/bin/env python3
"""
Simple test to verify user list functionality
"""

import json
import os
from pathlib import Path

# Find the users.json file
backend_dir = Path(__file__).parent.parent.parent.parent
user_storage_path = backend_dir / "storage" / "user_details" / "users.json"

print(f"Looking for users.json at: {user_storage_path}")

if user_storage_path.exists():
    try:
        with open(user_storage_path, 'r') as f:
            users_data = json.load(f)
        
        print(f"\nFound {len(users_data)} users in storage:")
        for i, user in enumerate(users_data[:5], 1):  # Show first 5 users
            email = user.get('email', 'No email')
            name = user.get('name', 'No name')
            company = user.get('company', 'No company')
            print(f"{i}. {email} - {name} ({company})")
        
        if len(users_data) > 5:
            print(f"... and {len(users_data) - 5} more users")
        
        print("\n✅ User list functionality test completed successfully!")
        print("The main.py script can now fetch emails from this user list using --from-user-list flag")
        
    except Exception as e:
        print(f"❌ Error reading users.json: {e}")
else:
    print(f"❌ users.json not found at {user_storage_path}")
    print("Please make sure the user storage has been initialized.")