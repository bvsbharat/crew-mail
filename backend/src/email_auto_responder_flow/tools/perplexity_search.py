import os
import requests
from typing import Optional, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class PerplexitySearchInput(BaseModel):
    """Input schema for Perplexity search tool."""
    query: str = Field(..., description="Search query for finding user information")


class PerplexitySearchTool(BaseTool):
    name: str = "Perplexity Search"
    description: str = (
        "Search for professional information about a person using Perplexity AI. "
        "Useful for finding detailed professional background, bio, company information, "
        "and social media profiles. Input should be a person's name and email."
    )
    args_schema: type[BaseModel] = PerplexitySearchInput

    def _run(self, query: str) -> str:
        """Execute Perplexity search for user information."""
        api_key = os.getenv("SONAR_API_KEY")
        if not api_key:
            return "Error: SONAR_API_KEY not found in environment variables"

        try:
            # Enhanced prompt for better user profile generation
            enhanced_query = f"""
            Find detailed professional information about: {query}
            
            Please provide:
            1. Full name and current job title
            2. Company name and industry
            3. Professional bio (2-3 sentences)
            4. LinkedIn profile URL
            5. Twitter/X profile URL (if available)
            6. Personal website (if available)
            7. Location (city, country)
            8. Key achievements or notable work
            9. Educational background (if available)
            10. Any other relevant professional information
            
            Format the response clearly with labeled sections.
            """

            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'sonar-pro',
                    'messages': [
                        {
                            'role': 'user',
                            'content': enhanced_query
                        }
                    ],
                    'temperature': 0.1,
                    'max_tokens': 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return f"Perplexity Search Results for {query}:\n\n{content}"
                else:
                    return f"No results found for {query}"
            else:
                return f"Error: Perplexity API returned status code {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return "Error: Request to Perplexity API timed out"
        except requests.exceptions.RequestException as e:
            return f"Error: Request failed - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"