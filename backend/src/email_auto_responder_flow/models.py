from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Email(BaseModel):
    id: str
    threadId: str
    snippet: str
    sender: str
    subject: str = "No Subject"
    body: str = ""


class UserDetails(BaseModel):
    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    source: str = "exa"


class UserSearchRequest(BaseModel):
    email: str
    name: Optional[str] = None
    force_refresh: bool = False
