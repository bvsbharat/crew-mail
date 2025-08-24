#!/usr/bin/env python
import time
from typing import List

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from email_auto_responder_flow.models import Email
from email_auto_responder_flow.utils.emails import check_email, format_emails

from .crews.email_filter_crew.email_filter_crew import EmailFilterCrew
from .crews.user_details_crew.user_details_crew import UserDetailsCrew


class AutoResponderState(BaseModel):
    id: str = "auto_responder_flow"
    emails: List[Email] = []
    checked_emails_ids: set[str] = set()
    user_details_processed: set[str] = set()


class EmailAutoResponderFlow(Flow[AutoResponderState]):
    initial_state = AutoResponderState

    @start("wait_next_run")
    def fetch_new_emails(self):
        print("Kickoff the Email Filter Crew")
        new_emails, updated_checked_email_ids = check_email(
            checked_emails_ids=self.state.checked_emails_ids
        )

        self.state.emails = new_emails
        self.state.checked_emails_ids = updated_checked_email_ids

    @listen(fetch_new_emails)
    def fetch_user_details(self):
        print("Fetching user details for new emails")
        if len(self.state.emails) > 0:
            user_details_crew = UserDetailsCrew()
            
            for email in self.state.emails:
                # Extract sender email from the sender field
                sender_email = email.sender
                if "<" in sender_email and ">" in sender_email:
                    # Extract email from "Name <email@domain.com>" format
                    sender_email = sender_email.split("<")[1].split(">")[0].strip()
                elif " " in sender_email:
                    # If there's a space, take the last part as email
                    sender_email = sender_email.split()[-1]
                
                # Extract sender name if available
                sender_name = None
                if "<" in email.sender:
                    sender_name = email.sender.split("<")[0].strip()
                elif " " in email.sender and "@" not in email.sender.split()[0]:
                    sender_name = " ".join(email.sender.split()[:-1])
                
                # Only fetch user details if we haven't processed this sender before
                if sender_email not in self.state.user_details_processed:
                    try:
                        print(f"Fetching user details for: {sender_email}")
                        user_details = user_details_crew.fetch_user_details(
                            email=sender_email,
                            name=sender_name,
                            force_refresh=False
                        )
                        self.state.user_details_processed.add(sender_email)
                        print(f"User details fetched for {sender_email}: {user_details.name or 'Unknown'} at {user_details.company or 'Unknown company'}")
                    except Exception as e:
                        print(f"Error fetching user details for {sender_email}: {str(e)}")
                        # Add to processed set even if failed to avoid retrying immediately
                        self.state.user_details_processed.add(sender_email)

    @listen(fetch_user_details)
    def generate_draft_responses(self):
        print("Current email queue: ", len(self.state.emails))
        if len(self.state.emails) > 0:
            print("Writing New emails")
            emails = format_emails(self.state.emails)

            EmailFilterCrew().crew().kickoff(inputs={"emails": emails})

            self.state.emails = []

        print("Waiting for 180 seconds")
        time.sleep(180)


def kickoff():
    """
    Run the flow.
    """
    email_auto_response_flow = EmailAutoResponderFlow()
    email_auto_response_flow.kickoff()


def plot_flow():
    """
    Plot the flow.
    """
    email_auto_response_flow = EmailAutoResponderFlow()
    email_auto_response_flow.plot()


if __name__ == "__main__":
    kickoff()
    
