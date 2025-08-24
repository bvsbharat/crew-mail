import re
from typing import Optional, Tuple
from email_auto_responder_flow.utils.user_storage import UserStorage
from email_auto_responder_flow.crews.user_details_crew.user_details_crew import UserDetailsCrew


class EmailUserIntegration:
    """Handles integration between email processing and user details fetching."""
    
    def __init__(self):
        self.user_storage = UserStorage()
        self.user_details_crew = UserDetailsCrew()
    
    def extract_email_and_name(self, sender_field: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract email and name from sender field."""
        if not sender_field:
            return None, None
        
        # Pattern: "Name <email@domain.com>" or just "email@domain.com"
        email_pattern = r'<([^>]+)>'
        name_pattern = r'^([^<]+)<'
        
        email_match = re.search(email_pattern, sender_field)
        name_match = re.search(name_pattern, sender_field)
        
        if email_match:
            email = email_match.group(1).strip()
            name = name_match.group(1).strip() if name_match else None
        elif '@' in sender_field:
            email = sender_field.strip()
            name = None
        else:
            return None, None
        
        return email, name
    
    def should_fetch_user_details(self, email: str, name: Optional[str] = None) -> bool:
        """Check if user details should be fetched."""
        if not email or '@' not in email:
            return False
        
        # Don't fetch for common system emails
        system_domains = ['noreply', 'no-reply', 'donotreply', 'calendar', 'notification']
        email_lower = email.lower()
        
        for domain in system_domains:
            if domain in email_lower:
                return False
        
        # Check if user already exists
        return not self.user_storage.user_exists(email, name)
    
    async def process_email_for_user_details(self, sender_field: str) -> Optional[str]:
        """Process email sender and trigger user details fetching if needed."""
        email, name = self.extract_email_and_name(sender_field)
        
        if not email:
            return None
        
        if self.should_fetch_user_details(email, name):
            try:
                # Fetch user details in background
                user_details = self.user_details_crew.fetch_user_details(email, name, force_refresh=False)
                return f"User details fetched for {email}"
            except Exception as e:
                print(f"Error fetching user details for {email}: {e}")
                return f"Error fetching user details for {email}"
        
        return f"User details already exist for {email}"
