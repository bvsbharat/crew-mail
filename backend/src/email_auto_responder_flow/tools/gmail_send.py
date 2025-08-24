import os
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.send_message import GmailSendMessage


class GmailSendInput(BaseModel):
    """Input schema for GmailSendTool."""
    data: str = Field(..., description="Pipe (|) separated text of length 3: email|subject|message")


class GmailSendTool(BaseTool):
    name: str = "Send Gmail"
    description: str = "Useful to send an email via Gmail. The input to this tool should be a pipe (|) separated text of length 3 (three), representing who to send the email to, the subject of the email and the actual message. For example, `lorem@ipsum.com|Nice To Meet You|Hey it was great to meet you.`."
    args_schema: Type[BaseModel] = GmailSendInput

    def _run(self, data: str) -> str:
        """
        Send an email via Gmail.
        """
        email, subject, message = data.split("|")
        
        # Get the path to credentials.json in the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..', '..')
        credentials_path = os.path.join(project_root, 'credentials.json')
        
        # Rebuild the GmailToolkit model to resolve Pydantic issues
        GmailToolkit.model_rebuild()
        
        gmail = GmailToolkit(credentials_path=credentials_path)
        sender = GmailSendMessage(api_resource=gmail.api_resource)
        result = sender({"to": [email], "subject": subject, "message": message})
        return f"\nEmail sent: {result}\n"