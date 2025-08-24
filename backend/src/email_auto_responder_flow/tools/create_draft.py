import os
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.create_draft import GmailCreateDraft


class CreateDraftInput(BaseModel):
    """Input schema for CreateDraftTool."""
    data: str = Field(..., description="Pipe (|) separated text of length 3: email|subject|message")


class CreateDraftTool(BaseTool):
    name: str = "Create Draft"
    description: str = "Useful to create an email draft. The input to this tool should be a pipe (|) separated text of length 3 (three), representing who to send the email to, the subject of the email and the actual message. For example, `lorem@ipsum.com|Nice To Meet You|Hey it was great to meet you.`."
    args_schema: Type[BaseModel] = CreateDraftInput

    def _run(self, data: str) -> str:
        """
        Create an email draft.
        """
        email, subject, message = data.split("|")
        
        # Get the path to credentials.json in the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..', '..')
        credentials_path = os.path.join(project_root, 'credentials.json')
        
        # Rebuild the GmailToolkit model to resolve Pydantic issues
        GmailToolkit.model_rebuild()
        
        gmail = GmailToolkit(credentials_path=credentials_path)
        draft = GmailCreateDraft(api_resource=gmail.api_resource)
        result = draft({"to": [email], "subject": subject, "message": message})
        return f"\nDraft created: {result}\n"
