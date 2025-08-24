import os
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.get_thread import GmailGetThread


class GmailThreadInput(BaseModel):
    """Input schema for GmailThreadTool."""
    thread_id: str = Field(..., description="The Gmail thread ID to retrieve")


class GmailThreadTool(BaseTool):
    name: str = "Get Gmail Thread"
    description: str = "Useful to get a Gmail thread by its ID. The input should be a thread ID string. Returns the thread content and messages."
    args_schema: Type[BaseModel] = GmailThreadInput

    def _run(self, thread_id: str) -> str:
        """
        Get a Gmail thread by its ID.
        """
        # Get the path to credentials.json in the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..', '..')
        credentials_path = os.path.join(project_root, 'credentials.json')
        
        # Rebuild the GmailToolkit model to resolve Pydantic issues
        GmailToolkit.model_rebuild()
        
        gmail = GmailToolkit(credentials_path=credentials_path)
        thread_getter = GmailGetThread(api_resource=gmail.api_resource)
        result = thread_getter.run(thread_id)
        return f"\nThread content: {result}\n"