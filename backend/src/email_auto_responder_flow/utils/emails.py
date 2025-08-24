import os
import time
from typing import List

from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.search import GmailSearch

from email_auto_responder_flow.models import Email
from email_auto_responder_flow.utils.storage import save_emails_to_file, load_emails_from_file


def check_email(checked_emails_ids: set[str]) -> tuple[list[Email], set[str]]:
    print("# Checking for new emails")

    try:
        # Get the path to credentials.json in the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
        credentials_path = os.path.join(project_root, 'credentials.json')
        
        print(f"Looking for credentials at: {credentials_path}")
        if not os.path.exists(credentials_path):
            print(f"Credentials file not found at {credentials_path}")
            return [], checked_emails_ids
        
        # Rebuild the GmailToolkit model to resolve Pydantic issues
        GmailToolkit.model_rebuild()
        
        gmail = GmailToolkit(credentials_path=credentials_path)
        search = GmailSearch(api_resource=gmail.api_resource)
    except Exception as e:
        print(f"Error initializing Gmail toolkit: {e}")
        print("Please ensure you have proper Gmail API credentials set up.")
        return [], checked_emails_ids
    # Search for emails in primary inbox only, limit to first 5
    emails = search.invoke({"query": "in:inbox category:primary"})
    print(f"Total emails found: {len(emails)}")
    
    # Limit to first 5 emails
    emails = emails[:5] if len(emails) > 5 else emails
    print(f"Processing first {len(emails)} emails")
    
    thread = []
    new_emails: List[Email] = []
    for email in emails:
        print(f"Processing email from: {email.get('sender', 'Unknown')} - Subject: {email.get('snippet', 'No snippet')[:50]}...")
        if (
            (email["id"] not in checked_emails_ids)
            and (email["threadId"] not in thread)
            and (os.environ["MY_EMAIL"] not in email["sender"])
        ):
            thread.append(email["threadId"])
            new_emails.append(
                Email(
                    id=email["id"],
                    threadId=email["threadId"],
                    snippet=email["snippet"],
                    sender=email["sender"],
                    subject=email.get("subject", "No Subject"),
                    body=email.get("body", email["snippet"]),
                )
            )
    checked_emails_ids.update([email["id"] for email in emails])
    
    # Save new emails to file storage
    if new_emails:
        save_emails_to_file(new_emails)
        print(f"Saved {len(new_emails)} new emails to file storage")
    
    return new_emails, checked_emails_ids


def wait_next_run(state):
    print("## Waiting for 180 seconds")
    time.sleep(180)
    return state


def new_emails(state):
    if len(state["emails"]) == 0:
        print("## No new emails")
        return "end"
    else:
        print("## New emails")
        return "continue"


def format_emails(emails):
    emails_string = []
    for email in emails:
        print(email)
        arr = [
            f"ID: {email.id}",
            f"- Thread ID: {email.threadId}",
            f"- Snippet: {email.snippet}",
            f"- From: {email.sender}",
            "--------",
        ]
        emails_string.append("\n".join(arr))
    return "\n".join(emails_string)
