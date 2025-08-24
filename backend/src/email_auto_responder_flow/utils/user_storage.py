import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from email_auto_responder_flow.models import UserDetails


class UserStorage:
    """Handles file system storage for user details."""
    
    def __init__(self, storage_path: str = "storage/user_details"):
        self.storage_path = Path(storage_path)
        self.users_file = self.storage_path / "users.json"
        self.profiles_dir = self.storage_path / "profiles"
        self.cache_dir = self.storage_path / "cache"
        
        # Create directories if they don't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.profiles_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize users file if it doesn't exist
        if not self.users_file.exists():
            self._save_users_index({})
    
    def _load_users_index(self) -> Dict[str, Any]:
        """Load the main users index file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users_index(self, users_data: Dict[str, Any]) -> None:
        """Save the main users index file."""
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=2, default=str)
    
    def user_exists(self, email: str, name: Optional[str] = None) -> bool:
        """Check if user already exists in storage."""
        users_index = self._load_users_index()
        
        # Check by email first
        if email in users_index:
            return True
        
        # If name is provided, check for name match with different email
        if name:
            for user_email, user_data in users_index.items():
                if user_data.get('name', '').lower() == name.lower():
                    return True
        
        return False
    
    def get_user_details(self, email: str) -> Optional[UserDetails]:
        """Retrieve user details by email."""
        users_index = self._load_users_index()
        
        if email not in users_index:
            return None
        
        user_data = users_index[email]
        profile_file = self.profiles_dir / f"{email.replace('@', '_at_').replace('.', '_')}.json"
        
        if profile_file.exists():
            with open(profile_file, 'r') as f:
                detailed_data = json.load(f)
                return UserDetails(**detailed_data)
        
        return UserDetails(**user_data)
    
    def save_user_details(self, user_details: UserDetails) -> bool:
        """Save user details to storage."""
        try:
            users_index = self._load_users_index()
            
            # Update index
            users_index[user_details.email] = {
                "email": user_details.email,
                "name": user_details.name,
                "company": user_details.company,
                "created_at": user_details.created_at.isoformat(),
                "updated_at": datetime.now().isoformat(),
                "source": user_details.source
            }
            
            # Save detailed profile
            profile_file = self.profiles_dir / f"{user_details.email.replace('@', '_at_').replace('.', '_')}.json"
            user_dict = user_details.model_dump()
            user_dict['updated_at'] = datetime.now().isoformat()
            
            with open(profile_file, 'w') as f:
                json.dump(user_dict, f, indent=2, default=str)
            
            # Update index
            self._save_users_index(users_index)
            
            return True
        except Exception as e:
            print(f"Error saving user details: {e}")
            return False
    
    def search_users(self, query: str) -> List[UserDetails]:
        """Search users by name, email, or company."""
        users_index = self._load_users_index()
        results = []
        
        query_lower = query.lower()
        
        for email, user_data in users_index.items():
            if (query_lower in email.lower() or 
                query_lower in (user_data.get('name', '') or '').lower() or
                query_lower in (user_data.get('company', '') or '').lower()):
                
                user_details = self.get_user_details(email)
                if user_details:
                    results.append(user_details)
        
        return results
    
    def get_all_users(self) -> List[UserDetails]:
        """Get all stored users."""
        users_index = self._load_users_index()
        results = []
        
        for email in users_index.keys():
            user_details = self.get_user_details(email)
            if user_details:
                results.append(user_details)
        
        return results
    
    def delete_user(self, email: str) -> bool:
        """Delete user from storage."""
        try:
            users_index = self._load_users_index()
            
            if email in users_index:
                del users_index[email]
                self._save_users_index(users_index)
                
                # Delete profile file
                profile_file = self.profiles_dir / f"{email.replace('@', '_at_').replace('.', '_')}.json"
                if profile_file.exists():
                    profile_file.unlink()
                
                return True
            return False
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
