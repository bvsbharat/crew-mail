import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

from email_auto_responder_flow.tools.exa_search import ExaSearchTool
from email_auto_responder_flow.tools.serper_search import SerperSearchTool
from email_auto_responder_flow.tools.perplexity_search import PerplexitySearchTool
from email_auto_responder_flow.utils.user_storage import UserStorage
from email_auto_responder_flow.models import UserDetails, UserSearchRequest
from datetime import datetime


@CrewBase
class UserDetailsCrew:
    """User Details Research Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="gpt-4o")

    def __init__(self):
        super().__init__()
        self.user_storage = UserStorage()

    @agent
    def user_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["user_research_agent"],
            tools=[ExaSearchTool(), SerperSearchTool(), PerplexitySearchTool()],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def serper_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["serper_research_agent"],
            tools=[SerperSearchTool(), PerplexitySearchTool()],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def data_validation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["data_validation_agent"],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    @task
    def research_user_details_task(self) -> Task:
        return Task(config=self.tasks_config["research_user_details"])

    @task
    def serper_research_task(self) -> Task:
        return Task(config=self.tasks_config["serper_research"])

    @task
    def validate_and_store_task(self) -> Task:
        return Task(config=self.tasks_config["validate_and_store"])

    @crew
    def crew(self) -> Crew:
        """Creates the User Details Research Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def fetch_user_details(self, email: str, name: str = None, force_refresh: bool = False) -> UserDetails:
        """Main method to fetch user details with uniqueness check."""
        
        # Check if user already exists and force_refresh is False
        if not force_refresh and self.user_storage.user_exists(email, name):
            existing_user = self.user_storage.get_user_details(email)
            if existing_user:
                return existing_user

        # Create search request
        search_request = UserSearchRequest(
            email=email,
            name=name,
            force_refresh=force_refresh
        )

        # Execute crew to research user details
        result = self.crew().kickoff(inputs={
            "email": email,
            "name": name or "Unknown",
            "search_query": f"{name} {email}" if name else email
        })

        # Parse result and create UserDetails object
        user_details = self._parse_crew_result(result, email, name)
        
        # Store the user details
        self.user_storage.save_user_details(user_details)
        
        return user_details

    def _parse_crew_result(self, result, email: str, name: str = None) -> UserDetails:
        """Parse crew result and create UserDetails object from EXA, Serper, and Perplexity data."""
        import re
        import json
        
        try:
            # Initialize default values
            company = None
            role = None
            bio = None
            linkedin_url = None
            twitter_url = None
            website = None
            location = None
            industry = None
            achievements = None
            
            # Convert CrewOutput to string if needed
            if hasattr(result, 'raw'):
                result_text = str(result.raw)
            else:
                result_text = str(result)
            
            # Try to extract structured information from the result
            result_lower = result_text.lower()
            
            print(f"Parsing result for {email}: {result_text[:500]}...")  # Debug log
            
            # Extract company information with enhanced patterns
            company_patterns = [
                r'company[:\s]*([^\n\r\.]+)',
                r'works at[:\s]*([^\n\r\.]+)',
                r'employed by[:\s]*([^\n\r\.]+)',
                r'currently at[:\s]*([^\n\r\.]+)',
                r'organization[:\s]*([^\n\r\.]+)',
                r'employer[:\s]*([^\n\r\.]+)'
            ]
            for pattern in company_patterns:
                match = re.search(pattern, result_lower)
                if match:
                    company = match.group(1).strip().title()
                    # Clean up common artifacts
                    company = re.sub(r'^(is|at|the)\s+', '', company, flags=re.IGNORECASE)
                    if len(company) > 3:  # Avoid single letters or very short matches
                        break
            
            # Extract role/title information with enhanced patterns
            role_patterns = [
                r'job title[:\s]*([^\n\r\.]+)',
                r'title[:\s]*([^\n\r\.]+)',
                r'position[:\s]*([^\n\r\.]+)',
                r'role[:\s]*([^\n\r\.]+)',
                r'current role[:\s]*([^\n\r\.]+)',
                r'works as[:\s]*([^\n\r\.]+)',
                r'serves as[:\s]*([^\n\r\.]+)'
            ]
            for pattern in role_patterns:
                match = re.search(pattern, result_lower)
                if match:
                    role = match.group(1).strip().title()
                    # Clean up common artifacts
                    role = re.sub(r'^(is|a|an|the)\s+', '', role, flags=re.IGNORECASE)
                    if len(role) > 3:  # Avoid single letters or very short matches
                        break
            
            # Extract LinkedIn URL
            linkedin_match = re.search(r'linkedin\.com/in/([^\s\n\r]+)', result_lower)
            if linkedin_match:
                linkedin_url = f"https://linkedin.com/in/{linkedin_match.group(1)}"
            
            # Extract Twitter URL
            twitter_match = re.search(r'twitter\.com/([^\s\n\r]+)', result_lower)
            if twitter_match:
                twitter_url = f"https://twitter.com/{twitter_match.group(1)}"
            
            # Extract website URL
            website_patterns = [
                r'website[:\s]+(https?://[^\s\n\r]+)',
                r'personal site[:\s]+(https?://[^\s\n\r]+)',
                r'portfolio[:\s]+(https?://[^\s\n\r]+)'
            ]
            for pattern in website_patterns:
                match = re.search(pattern, result_lower)
                if match:
                    website = match.group(1)
                    break
            
            # Extract location
            location_patterns = [
                r'location[:\s]+([^\n\r]+)',
                r'based in[:\s]+([^\n\r]+)',
                r'lives in[:\s]+([^\n\r]+)'
            ]
            for pattern in location_patterns:
                match = re.search(pattern, result_lower)
                if match:
                    location = match.group(1).strip().title()
                    break
            
            # Extract industry
            industry_patterns = [
                r'industry[:\s]+([^\n\r]+)',
                r'sector[:\s]+([^\n\r]+)',
                r'field[:\s]+([^\n\r]+)'
            ]
            for pattern in industry_patterns:
                match = re.search(pattern, result_lower)
                if match:
                    industry = match.group(1).strip().title()
                    break
            
            # Extract bio/summary with enhanced patterns for comprehensive professional information
            bio_patterns = [
                r'professional bio[:\s]*([^\n\r]{50,400})',
                r'bio[:\s]*([^\n\r]{50,400})',
                r'summary[:\s]*([^\n\r]{50,400})',
                r'about[:\s]*([^\n\r]{50,400})',
                r'background[:\s]*([^\n\r]{50,400})',
                r'profile[:\s]*([^\n\r]{50,400})',
                r'description[:\s]*([^\n\r]{50,400})'
            ]
            for pattern in bio_patterns:
                match = re.search(pattern, result_lower)
                if match:
                    bio = match.group(1).strip()
                    # Clean up the bio
                    bio = re.sub(r'^(is|a|an|the)\s+', '', bio, flags=re.IGNORECASE)
                    bio = bio.strip('.,;:')
                    if len(bio) > 50:  # Ensure we have substantial content
                        break
            
            # If no structured bio found, try to extract from general text
            if not bio:
                # Look for sentences that describe the person professionally
                sentences = re.split(r'[.!?]+', result_text)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if (len(sentence) > 50 and 
                        any(keyword in sentence.lower() for keyword in 
                            ['experience', 'expert', 'professional', 'specializes', 'focuses', 'leads', 'manages', 'develops', 'works'])):
                        bio = sentence.strip()
                        break
            
            # Extract achievements/notable work
            achievement_patterns = [
                r'achievements?[:\s]*([^\n\r]{30,300})',
                r'notable work[:\s]*([^\n\r]{30,300})',
                r'accomplishments?[:\s]*([^\n\r]{30,300})',
                r'key projects?[:\s]*([^\n\r]{30,300})'
            ]
            for pattern in achievement_patterns:
                match = re.search(pattern, result_lower)
                if match:
                    achievements = match.group(1).strip()
                    break
            
            # Combine bio and achievements if both exist
            if bio and achievements:
                bio = f"{bio}. Notable achievements: {achievements}"
            elif achievements and not bio:
                bio = f"Notable achievements: {achievements}"
            
            return UserDetails(
                email=email,
                name=name,
                company=company,
                role=role,
                bio=bio,
                linkedin_url=linkedin_url,
                twitter_url=twitter_url,
                website=website,
                location=location,
                industry=industry,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                source="exa+serper+perplexity"
            )
            
        except Exception as e:
            print(f"Error parsing crew result: {e}")
            return UserDetails(
                email=email,
                name=name,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                source="exa+serper+perplexity"
            )
