import json
import os
from datetime import datetime
from typing import List, Dict, Any, Union
from email_auto_responder_flow.models import Email

# Get the storage directory path
def get_storage_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
    storage_dir = os.path.join(project_root, 'storage')
    
    # Create storage directory if it doesn't exist
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
    
    return storage_dir

def save_emails_to_file(emails: List[Email]) -> bool:
    """Save emails to the storage file"""
    try:
        storage_path = get_storage_path()
        emails_file = os.path.join(storage_path, 'emails.json')
        
        # Load existing emails as dictionaries
        existing_emails_raw = load_emails_from_file_raw()
        existing_ids = {email.get('id') for email in existing_emails_raw}
        
        # Add new emails (avoid duplicates)
        new_emails = []
        for email in emails:
            email_id = email.id if hasattr(email, 'id') else email.get('id')
            if email_id not in existing_ids:
                # Convert Email object to dictionary and add timestamp
                if isinstance(email, Email):
                    email_data = email.model_dump()
                else:
                    email_data = dict(email)
                email_data['fetched_at'] = datetime.now().isoformat()
                new_emails.append(email_data)
        
        # Combine existing and new emails
        all_emails = existing_emails_raw + new_emails
        
        # Save to file
        with open(emails_file, 'w', encoding='utf-8') as f:
            json.dump(all_emails, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(new_emails)} new emails to storage. Total: {len(all_emails)}")
        return True
        
    except Exception as e:
        print(f"Error saving emails to file: {e}")
        return False

def load_emails_from_file_raw() -> List[Dict[str, Any]]:
    """Load emails from the storage file as raw dictionaries"""
    try:
        storage_path = get_storage_path()
        emails_file = os.path.join(storage_path, 'emails.json')
        
        if not os.path.exists(emails_file):
            return []
        
        with open(emails_file, 'r', encoding='utf-8') as f:
            emails = json.load(f)
        
        return emails
        
    except Exception as e:
        print(f"Error loading emails from file: {e}")
        return []

def load_emails_from_file() -> List[Email]:
    """Load emails from the storage file as Email objects"""
    try:
        emails_raw = load_emails_from_file_raw()
        emails = []
        
        for email_data in emails_raw:
            try:
                # Convert dictionary to Email object
                email = Email(**email_data)
                emails.append(email)
            except Exception as e:
                print(f"Error converting email data to Email object: {e}")
                print(f"Email data: {email_data}")
                continue
        
        return emails
        
    except Exception as e:
        print(f"Error loading emails from file: {e}")
        return []

def save_draft_to_file(draft_data: Dict[str, Any]) -> bool:
    """Save a draft response to the storage file"""
    try:
        storage_path = get_storage_path()
        drafts_file = os.path.join(storage_path, 'drafts.json')
        
        # Load existing drafts
        existing_drafts = load_drafts_from_file()
        
        # Add timestamp and unique ID
        draft_data['created_at'] = datetime.now().isoformat()
        draft_data['draft_id'] = f"draft_{len(existing_drafts) + 1}_{int(datetime.now().timestamp())}"
        
        # Add new draft
        existing_drafts.append(draft_data)
        
        # Save to file
        with open(drafts_file, 'w', encoding='utf-8') as f:
            json.dump(existing_drafts, f, indent=2, ensure_ascii=False)
        
        print(f"Saved draft response to storage. Draft ID: {draft_data['draft_id']}")
        return True
        
    except Exception as e:
        print(f"Error saving draft to file: {e}")
        return False

def load_drafts_from_file() -> List[Dict[str, Any]]:
    """Load draft responses from the storage file"""
    try:
        storage_path = get_storage_path()
        drafts_file = os.path.join(storage_path, 'drafts.json')
        
        if not os.path.exists(drafts_file):
            return []
        
        with open(drafts_file, 'r', encoding='utf-8') as f:
            drafts = json.load(f)
        
        return drafts
        
    except Exception as e:
        print(f"Error loading drafts from file: {e}")
        return []

def clear_emails_storage() -> bool:
    """Clear all emails from storage"""
    try:
        storage_path = get_storage_path()
        emails_file = os.path.join(storage_path, 'emails.json')
        
        with open(emails_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        print("Cleared all emails from storage")
        return True
        
    except Exception as e:
        print(f"Error clearing emails storage: {e}")
        return False

def clear_drafts_storage() -> bool:
    """Clear all drafts from storage"""
    try:
        storage_path = get_storage_path()
        drafts_file = os.path.join(storage_path, 'drafts.json')
        
        with open(drafts_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        print("Cleared all drafts from storage")
        return True
        
    except Exception as e:
        print(f"Error clearing drafts storage: {e}")
        return False