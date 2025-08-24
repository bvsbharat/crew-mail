import os
from typing import Optional, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests
import json


class SerperSearchInput(BaseModel):
    """Input schema for Serper search tool."""
    query: str = Field(..., description="Search query for finding user information")
    num_results: int = Field(default=10, description="Number of results to return")
    search_type: str = Field(default="search", description="Type of search: search, images, news, etc.")
    country: str = Field(default="us", description="Country code for search results")
    language: str = Field(default="en", description="Language for search results")


class SerperSearchTool(BaseTool):
    name: str = "serper_search"
    description: str = (
        "Search for professional information about a person using Serper Google Search API. "
        "Useful for finding LinkedIn profiles, company information, news articles, and professional details."
    )
    args_schema: type[BaseModel] = SerperSearchInput

    def _run(self, query: str, num_results: int = 10, search_type: str = "search", 
             country: str = "us", language: str = "en") -> str:
        """Execute the Serper search."""
        try:
            serper_api_key = os.getenv("SERPER_API_KEY")
            if not serper_api_key:
                return "Error: SERPER_API_KEY not found in environment variables"

            url = f"https://google.serper.dev/{search_type}"
            headers = {
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "q": query,
                "num": num_results,
                "gl": country,
                "hl": language
            }

            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                return json.dumps(results, indent=2)
            else:
                return f"Error: Serper API request failed with status {response.status_code}: {response.text}"

        except Exception as e:
            return f"Error executing Serper search: {str(e)}"