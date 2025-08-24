#!/usr/bin/env python3
import os

# Simulate the path calculation from emails.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '.'))
credentials_path = os.path.join(project_root, 'credentials.json')

print(f"Current directory: {current_dir}")
print(f"Project root: {project_root}")
print(f"Credentials path: {credentials_path}")
print(f"Credentials file exists: {os.path.exists(credentials_path)}")

if os.path.exists(credentials_path):
    print("✅ Credentials file found successfully!")
else:
    print("❌ Credentials file not found!")
    print("Files in project root:")
    for item in os.listdir(project_root):
        print(f"  - {item}")