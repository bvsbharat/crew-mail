import os
from typing import Optional, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
import json


class ExaSearchInput(BaseModel):
    """Input schema for EXA search tool."""
    query: str = Field(..., description="Search query for finding user information")
    num_results: int = Field(default=5, description="Number of results to return")
    include_domains: Optional[str] = Field(default=None, description="Comma-separated domains to include")


class ExaSearchTool(BaseTool):
    name: str = "exa_search"
    description: str = (
        "Search for professional information about a person using EXA API. "
        "Useful for finding LinkedIn profiles, company information, and professional details."
    )
    args_schema: type[BaseModel] = ExaSearchInput

    def _run(self, query: str, num_results: int = 5, include_domains: Optional[str] = None) -> str:
        """Execute the EXA search."""
        try:
            exa_api_key = os.getenv("EXA_API_KEY")
            if not exa_api_key:
                return "Error: EXA_API_KEY not found in environment variables"

            url = "https://api.exa.ai/search"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "x-api-key": exa_api_key
            }

            payload = {
                "query": query,
                "numResults": num_results,
                "contents": {
                    "text": True,
                    "highlights": True,
                    "summary": True
                },
                "useAutoprompt": True,
                "type": "neural"
            }

            if include_domains:
                payload["includeDomains"] = include_domains.split(",")

            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                return json.dumps(results, indent=2)
            else:
                return f"Error: EXA API request failed with status {response.status_code}: {response.text}"

        except Exception as e:
            return f"Error executing EXA search: {str(e)}"
