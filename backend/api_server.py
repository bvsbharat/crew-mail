#!/usr/bin/env python
import os
import sys
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from datetime import datetime
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from email_auto_responder_flow.utils.emails import check_email, format_emails
from email_auto_responder_flow.models import Email, UserDetails, UserSearchRequest
from email_auto_responder_flow.tools.create_draft import CreateDraftTool
from email_auto_responder_flow.crews.email_filter_crew.email_filter_crew import EmailFilterCrew
from email_auto_responder_flow.crews.user_details_crew.user_details_crew import UserDetailsCrew
from email_auto_responder_flow.utils.storage import load_emails_from_file, save_draft_to_file, load_drafts_from_file, load_emails_from_file_raw
from email_auto_responder_flow.utils.user_storage import UserStorage
from email_auto_responder_flow.main import EmailAutoResponderFlow, AutoResponderState

app = FastAPI(title="Email Auto Responder API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state to track checked emails
checked_emails_ids: set[str] = set()

# Global state for CrewAI flow management
active_flows: Dict[str, EmailAutoResponderFlow] = {}
flow_status: Dict[str, Dict[str, Any]] = {}

# Initialize user storage
user_storage = UserStorage()
user_details_crew = UserDetailsCrew()

# Response models
class ApiEmail(BaseModel):
    id: str
    threadId: str
    subject: str
    sender: str
    recipient: str
    body: str
    snippet: str
    timestamp: str
    labels: List[str]
    is_read: bool
    is_important: bool
    drafts: Optional[List[Dict[str, Any]]] = []

class EmailBatch(BaseModel):
    emails: List[ApiEmail]
    total_count: int
    has_more: bool
    next_page_token: Optional[str] = None

class DraftRequest(BaseModel):
    to: str
    subject: str
    message: str

class DraftResponse(BaseModel):
    success: bool
    message: str
    draft_id: Optional[str] = None

class AgentDraftRequest(BaseModel):
    emails: List[Email]

class HealthResponse(BaseModel):
    status: str
    service: str

# CrewAI Flow Models
class FlowStartRequest(BaseModel):
    flow_id: Optional[str] = None
    auto_mode: bool = False

class FlowStatusResponse(BaseModel):
    flow_id: str
    status: str  # "running", "stopped", "error"
    emails_processed: int
    last_run: Optional[str] = None
    error_message: Optional[str] = None

class EmailAnalysisRequest(BaseModel):
    emails: List[Email]
    analysis_type: str = "filter"  # "filter", "priority", "sentiment"

class EmailAnalysisResponse(BaseModel):
    success: bool
    analysis_results: Dict[str, Any]
    processed_count: int
    recommendations: List[str]

class AutoResponseRequest(BaseModel):
    email_id: str
    thread_id: str
    context: Optional[str] = None
    response_type: str = "auto"  # "auto", "draft", "immediate"

class AutoResponseResponse(BaseModel):
    success: bool
    response_generated: bool
    draft_created: bool
    response_content: Optional[str] = None
    draft_id: Optional[str] = None

class SendEmailRequest(BaseModel):
    to: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    subject: str
    content: str
    from_email: Optional[str] = None
    reply_to_id: Optional[str] = None

class SendEmailResponse(BaseModel):
    success: bool
    message: str
    email_id: Optional[str] = None

class UserDetailsResponse(BaseModel):
    success: bool
    user_details: Optional[UserDetails] = None
    message: str
    from_cache: bool = False

class UserSearchResponse(BaseModel):
    success: bool
    users: List[UserDetails]
    total_count: int
    message: str

def convert_to_api_email(email: Email) -> ApiEmail:
    """Convert internal Email type to API Email format"""
    # Use actual subject if available, fallback to snippet extraction
    subject = getattr(email, 'subject', None) or (email.snippet.split('\n')[0][:100] if email.snippet else "No Subject")
    
    # Use environment variable for recipient or default
    recipient = os.getenv('MY_EMAIL', 'user@example.com')
    
    # Use current timestamp as fallback
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    return ApiEmail(
        id=email.id,
        threadId=email.threadId,
        subject=subject,
        sender=email.sender,
        recipient=recipient,
        body=email.snippet,  # Use snippet as body for now
        snippet=email.snippet,
        timestamp=timestamp,
        labels=[],
        is_read=False,
        is_important=False
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", service="Email Auto Responder API")

def create_mock_emails() -> List[ApiEmail]:
    """Create mock emails for demo purposes"""
    from datetime import datetime, timedelta
    import random
    
    mock_emails = [
        {
            "id": "mock_1",
            "threadId": "thread_1",
            "subject": "Welcome to our platform!",
            "sender": "Sarah Johnson <sarah@company.com>",
            "snippet": "Thank you for joining our platform. We're excited to have you on board and look forward to helping you achieve your goals.",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
        },
        {
            "id": "mock_2",
            "threadId": "thread_2",
            "subject": "Project Update - Q4 Planning",
            "sender": "Mike Chen <mike.chen@work.com>",
            "snippet": "Hi team, I wanted to share the latest updates on our Q4 planning. We've made significant progress on the roadmap.",
            "timestamp": (datetime.now() - timedelta(hours=5)).isoformat()
        },
        {
            "id": "mock_3",
            "threadId": "thread_3",
            "subject": "Meeting Reminder: Design Review",
            "sender": "Calendar <calendar@company.com>",
            "snippet": "This is a reminder that you have a design review meeting scheduled for tomorrow at 2:00 PM.",
            "timestamp": (datetime.now() - timedelta(hours=8)).isoformat()
        },
        {
            "id": "mock_4",
            "threadId": "thread_4",
            "subject": "Invoice #12345 - Payment Due",
            "sender": "Billing Team <billing@service.com>",
            "snippet": "Your invoice #12345 for $299.99 is now due. Please process payment by the end of this week.",
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            "id": "mock_5",
            "threadId": "thread_5",
            "subject": "New Feature Release Notes",
            "sender": "Product Team <product@company.com>",
            "snippet": "We're excited to announce the release of our new dashboard features. Check out what's new in this update.",
            "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
        }
    ]
    
    api_emails = []
    for email_data in mock_emails:
        api_emails.append(ApiEmail(
            id=email_data["id"],
            threadId=email_data["threadId"],
            subject=email_data["subject"],
            sender=email_data["sender"],
            recipient=os.getenv('MY_EMAIL', 'user@example.com'),
            body=email_data["snippet"],
            snippet=email_data["snippet"],
            timestamp=email_data["timestamp"],
            labels=[],
            is_read=random.choice([True, False]),
            is_important=random.choice([True, False])
        ))
    
    return api_emails

@app.get("/api/emails", response_model=EmailBatch)
async def get_emails(limit: int = 50):
    """Fetch emails from file storage with related drafts"""
    try:
        print(f"Fetching emails from storage with limit: {limit}")
        
        # Load emails from file storage as dictionaries
        stored_emails = load_emails_from_file_raw()
        print(f"Loaded {len(stored_emails)} emails from storage")
        
        # Load drafts from file storage
        drafts_data = load_drafts_from_file()
        print(f"Loaded {len(drafts_data)} drafts from storage")
        
        # Convert stored emails to API format and trigger user details fetching
        api_emails = []
        for email_data in stored_emails:
            # Extract sender email for user details lookup
            sender_email = email_data.get('sender', '')
            if sender_email and '<' in sender_email and '>' in sender_email:
                # Extract email from "Name <email@domain.com>" format
                sender_email = sender_email.split('<')[1].split('>')[0].strip()
            elif sender_email and '@' in sender_email:
                # Use as is if it's already just an email
                sender_email = sender_email.strip()
            
            # Trigger user details fetching in background if not exists
            if sender_email and '@' in sender_email:
                if not user_storage.user_exists(sender_email):
                    # Extract name from sender if available
                    sender_name = None
                    full_sender = email_data.get('sender', '')
                    if '<' in full_sender:
                        sender_name = full_sender.split('<')[0].strip()
                    
                    # Start background task to fetch user details
                    asyncio.create_task(fetch_user_details_background(sender_email, sender_name))
            # Find related drafts for this email
            related_drafts = []
            email_id = email_data.get('id', '')
            email_subject = email_data.get('snippet', '')[:100]
            email_sender = email_data.get('sender', '')
            
            for draft in drafts_data:
                # Check if draft is related to this email
                is_related = False
                
                # Check if draft.emails contains this email
                if 'emails' in draft and isinstance(draft['emails'], list):
                    for draft_email in draft['emails']:
                        if (isinstance(draft_email, dict) and 
                            (draft_email.get('id') == email_id or 
                             draft_email.get('sender') == email_sender)):
                            is_related = True
                            break
                
                # Fallback: check subject similarity
                if not is_related and 'formatted_emails' in draft:
                    if email_id in str(draft['formatted_emails']) or email_sender in str(draft['formatted_emails']):
                        is_related = True
                
                if is_related:
                    related_drafts.append({
                        'draft_id': draft.get('draft_id', ''),
                        'content': draft.get('agent_response', draft.get('message', '')),
                        'created_at': draft.get('created_at', draft.get('createdAt', '')),
                        'status': draft.get('status', 'draft'),
                        'response_type': draft.get('response_type', 'agent_generated')
                    })
            
            # Convert stored email data to ApiEmail format
            api_email = ApiEmail(
                id=email_data.get('id', ''),
                threadId=email_data.get('threadId', ''),
                subject=email_data.get('subject', 'No Subject'),
                sender=email_data.get('sender', 'Unknown'),
                recipient=os.getenv('MY_EMAIL', 'user@example.com'),
                body=email_data.get('body', email_data.get('snippet', '')),
                snippet=email_data.get('snippet', ''),
                timestamp=email_data.get('fetched_at', email_data.get('timestamp', '')),
                labels=[],
                is_read=False,
                is_important=False,
                drafts=related_drafts
            )
            api_emails.append(api_email)
        
        return EmailBatch(
            emails=api_emails[:limit],
            total_count=len(api_emails),
            has_more=len(api_emails) > limit
        )
    except Exception as e:
        print(f"Error in get_emails: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")

@app.post("/api/emails/draft", response_model=DraftResponse)
async def create_draft(draft_request: DraftRequest):
    """Create an email draft"""
    try:
        # Use the existing CreateDraftTool
        draft_tool = CreateDraftTool()
        data = f"{draft_request.to}|{draft_request.subject}|{draft_request.message}"
        result = draft_tool._run(data)
        
        return DraftResponse(
            success=True,
            message="Draft created successfully",
            draft_id=None  # Could extract from result if needed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create draft: {str(e)}")

@app.post("/api/emails/agent-draft", response_model=DraftResponse)
async def create_agent_draft(request: AgentDraftRequest):
    """Generate draft responses using the AI agent and save to storage"""
    try:
        if not request.emails:
            raise HTTPException(status_code=400, detail="No emails provided")
        
        print(f"Received {len(request.emails)} emails for draft generation")
        
        # Format emails for the crew
        formatted_emails = format_emails(request.emails)
        print(f"Formatted emails: {formatted_emails}")
        
        # Use the EmailFilterCrew to generate draft responses
        print("Initializing EmailFilterCrew...")
        crew = EmailFilterCrew()
        print("Starting crew kickoff...")
        result = crew.crew().kickoff(inputs={"emails": formatted_emails})
        print(f"Crew result: {result}")
        
        # Save draft to file storage
        draft_data = {
            "emails": [dict(email) for email in request.emails],
            "formatted_emails": formatted_emails,
            "agent_response": str(result),
            "response_type": "agent_generated",
            "status": "draft"
        }
        
        print(f"Saving draft data: {draft_data}")
        # Save to storage
        save_success = save_draft_to_file(draft_data)
        print(f"Save success: {save_success}")
        
        if save_success:
            return DraftResponse(
                success=True,
                message="Agent draft responses generated and saved successfully",
                draft_id=draft_data.get('draft_id')
            )
        else:
            return DraftResponse(
                success=False,
                message="Draft generated but failed to save to storage",
                draft_id=None
            )
            
    except Exception as e:
        print(f"Error in create_agent_draft: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate agent drafts: {str(e)}")

# CrewAI Flow Management Endpoints

@app.post("/api/flow/start", response_model=FlowStatusResponse)
async def start_email_flow(request: FlowStartRequest, background_tasks: BackgroundTasks):
    """Start the CrewAI email auto-responder flow"""
    try:
        flow_id = request.flow_id or f"flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if flow_id in active_flows:
            raise HTTPException(status_code=400, detail=f"Flow {flow_id} is already running")
        
        # Create new flow instance
        flow = EmailAutoResponderFlow()
        active_flows[flow_id] = flow
        
        # Initialize flow status
        flow_status[flow_id] = {
            "status": "running",
            "emails_processed": 0,
            "last_run": datetime.now().isoformat(),
            "error_message": None,
            "auto_mode": request.auto_mode
        }
        
        # Start flow in background if auto_mode is enabled
        if request.auto_mode:
            background_tasks.add_task(run_flow_background, flow_id, flow)
        
        return FlowStatusResponse(
            flow_id=flow_id,
            status="running",
            emails_processed=0,
            last_run=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start flow: {str(e)}")

@app.get("/api/flow/{flow_id}/status", response_model=FlowStatusResponse)
async def get_flow_status(flow_id: str):
    """Get the status of a specific flow"""
    if flow_id not in flow_status:
        raise HTTPException(status_code=404, detail=f"Flow {flow_id} not found")
    
    status = flow_status[flow_id]
    return FlowStatusResponse(
        flow_id=flow_id,
        status=status["status"],
        emails_processed=status["emails_processed"],
        last_run=status["last_run"],
        error_message=status.get("error_message")
    )

@app.post("/api/flow/{flow_id}/stop")
async def stop_flow(flow_id: str):
    """Stop a running flow"""
    if flow_id not in active_flows:
        raise HTTPException(status_code=404, detail=f"Flow {flow_id} not found")
    
    # Update status
    flow_status[flow_id]["status"] = "stopped"
    
    # Remove from active flows
    del active_flows[flow_id]
    
    return {"message": f"Flow {flow_id} stopped successfully"}

@app.get("/api/flow/list")
async def list_flows():
    """List all flows and their statuses"""
    return {
        "flows": [
            {
                "flow_id": flow_id,
                **status
            }
            for flow_id, status in flow_status.items()
        ]
    }

# Email Analysis Endpoints

@app.post("/api/emails/analyze", response_model=EmailAnalysisResponse)
async def analyze_emails(request: EmailAnalysisRequest):
    """Analyze emails using CrewAI agents"""
    try:
        if not request.emails:
            raise HTTPException(status_code=400, detail="No emails provided for analysis")
        
        # Format emails for analysis
        formatted_emails = format_emails(request.emails)
        
        # Create crew for analysis
        crew = EmailFilterCrew()
        
        # Run analysis based on type
        if request.analysis_type == "filter":
            result = crew.crew().kickoff(inputs={"emails": formatted_emails})
            analysis_results = {
                "filtered_emails": len(request.emails),
                "analysis_type": "filter",
                "crew_result": str(result)
            }
            recommendations = [
                "Review filtered emails for priority responses",
                "Consider automated responses for routine inquiries"
            ]
        else:
            # Placeholder for other analysis types
            analysis_results = {
                "analysis_type": request.analysis_type,
                "email_count": len(request.emails)
            }
            recommendations = ["Analysis completed"]
        
        return EmailAnalysisResponse(
            success=True,
            analysis_results=analysis_results,
            processed_count=len(request.emails),
            recommendations=recommendations
        )
    except Exception as e:
        print(f"Email analysis error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to analyze emails: {str(e)}")

@app.post("/api/emails/auto-respond", response_model=AutoResponseResponse)
async def generate_auto_response(request: AutoResponseRequest):
    """Generate automated response for a specific email"""
    try:
        # Get thread context if needed
        thread_content = None
        if request.thread_id:
            try:
                from email_auto_responder_flow.tools.gmail_thread import GmailThreadTool
                thread_tool = GmailThreadTool()
                thread_content = thread_tool._run(request.thread_id)
            except Exception as e:
                print(f"Warning: Could not fetch thread content: {e}")
        
        # Create mock email for processing
        mock_email = Email(
            id=request.email_id,
            threadId=request.thread_id,
            snippet=request.context or "Auto-response request",
            sender="user@example.com"
        )
        
        # Generate response using crew
        crew = EmailFilterCrew()
        formatted_email = format_emails([mock_email])
        
        if request.response_type == "draft":
            # Generate draft only
            result = crew.crew().kickoff(inputs={"emails": formatted_email})
            
            return AutoResponseResponse(
                success=True,
                response_generated=True,
                draft_created=True,
                response_content="Draft response generated by AI crew",
                draft_id=f"draft_{request.email_id}"
            )
        else:
            # Generate immediate response
            result = crew.crew().kickoff(inputs={"emails": formatted_email})
            
            return AutoResponseResponse(
                success=True,
                response_generated=True,
                draft_created=False,
                response_content="Automated response generated"
            )
    except Exception as e:
        print(f"Auto-response error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate auto-response: {str(e)}")

# Background task function
async def run_flow_background(flow_id: str, flow: EmailAutoResponderFlow):
    """Run the email flow in background"""
    try:
        while flow_id in active_flows and flow_status[flow_id]["status"] == "running":
            print(f"Running background flow {flow_id}...")
            
            # Use the proper CrewAI Flow kickoff method
            # This will trigger the entire flow including user details crew
            try:
                result = await flow.kickoff()
                print(f"Flow {flow_id} completed successfully")
                
                # Update flow status
                flow_status[flow_id]["last_run"] = datetime.now().isoformat()
                if hasattr(flow.state, 'emails') and flow.state.emails:
                    flow_status[flow_id]["emails_processed"] += len(flow.state.emails)
                    
            except Exception as flow_error:
                print(f"Flow {flow_id} execution error: {flow_error}")
                traceback.print_exc()
            
            # Wait before next check (reduced from 180s for demo)
            await asyncio.sleep(30)
    except Exception as e:
        flow_status[flow_id]["status"] = "error"
        flow_status[flow_id]["error_message"] = str(e)
        print(f"Flow {flow_id} error: {e}")
        traceback.print_exc()

@app.get("/api/emails/{email_id}", response_model=ApiEmail)
async def get_email_details(email_id: str):
    """Get detailed information for a specific email"""
    try:
        print(f"Fetching email details for ID: {email_id}")
        
        # Load emails from file storage
        stored_emails = load_emails_from_file_raw()
        
        # Find the specific email
        email_data = None
        for email in stored_emails:
            if email.get('id') == email_id:
                email_data = email
                break
        
        if not email_data:
            raise HTTPException(status_code=404, detail=f"Email with ID {email_id} not found")
        
        # Load drafts and find related ones
        drafts_data = load_drafts_from_file()
        related_drafts = []
        
        for draft in drafts_data:
            # Check if draft is related to this email
            is_related = False
            
            # Check if draft.emails contains this email
            if 'emails' in draft and isinstance(draft['emails'], list):
                for draft_email in draft['emails']:
                    if (isinstance(draft_email, dict) and 
                        (draft_email.get('id') == email_id or 
                         draft_email.get('sender') == email_data.get('sender'))):
                        is_related = True
                        break
            
            # Fallback: check subject similarity
            if not is_related and 'formatted_emails' in draft:
                if email_id in str(draft['formatted_emails']) or email_data.get('sender', '') in str(draft['formatted_emails']):
                    is_related = True
            
            if is_related:
                related_drafts.append({
                    'draft_id': draft.get('draft_id', ''),
                    'content': draft.get('agent_response', draft.get('message', '')),
                    'created_at': draft.get('created_at', draft.get('createdAt', '')),
                    'status': draft.get('status', 'draft'),
                    'response_type': draft.get('response_type', 'agent_generated')
                })
        
        # Convert to ApiEmail format
        api_email = ApiEmail(
            id=email_data.get('id', ''),
            threadId=email_data.get('threadId', ''),
            subject=email_data.get('subject', 'No Subject'),
            sender=email_data.get('sender', 'Unknown'),
            recipient=os.getenv('MY_EMAIL', 'user@example.com'),
            body=email_data.get('body', email_data.get('snippet', '')),
            snippet=email_data.get('snippet', ''),
            timestamp=email_data.get('fetched_at', email_data.get('timestamp', '')),
            labels=[],
            is_read=False,
            is_important=False,
            drafts=related_drafts
        )
        
        return api_email
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_email_details: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch email details: {str(e)}")

@app.get("/api/emails/unread", response_model=EmailBatch)
async def get_unread_emails(limit: int = 50):
    """Get unread emails (placeholder - uses same logic as get_emails for now)"""
    return await get_emails(limit)

@app.get("/api/emails/important", response_model=EmailBatch)
async def get_important_emails(limit: int = 50):
    """Get important emails (placeholder - uses same logic as get_emails for now)"""
    return await get_emails(limit)

@app.get("/api/drafts")
async def get_drafts():
    """Get all draft responses from storage"""
    try:
        drafts = load_drafts_from_file()
        return {
            "success": True,
            "drafts": drafts,
            "total_count": len(drafts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load drafts: {str(e)}")

@app.post("/api/emails/fetch")
async def fetch_emails_with_agent():
    """Trigger email fetching using CrewAI agent and save to storage"""
    try:
        global checked_emails_ids
        
        # Use the check_email function to fetch emails via CrewAI
        new_emails, updated_checked_ids = check_email(checked_emails_ids)
        checked_emails_ids = updated_checked_ids
        
        return {
            "success": True,
            "message": f"Fetched {len(new_emails)} new emails using CrewAI agent",
            "new_emails_count": len(new_emails),
            "total_checked": len(checked_emails_ids)
        }
        
    except Exception as e:
        print(f"Error fetching emails with agent: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")

@app.post("/api/emails/send", response_model=SendEmailResponse)
async def send_email(request: SendEmailRequest):
    """Send an email using Gmail API"""
    try:
        from email_auto_responder_flow.tools.gmail_send import GmailSendTool
        import uuid
        
        # Create Gmail send tool
        gmail_tool = GmailSendTool()
        
        # Prepare email data for the tool
        # Format: "to|subject|message" (3 parts as expected by Gmail tool)
        email_data = f"{request.to}|{request.subject}|{request.content}"
        
        # Send email using Gmail tool
        result = gmail_tool._run(email_data)
        
        # Generate a unique email ID for tracking
        email_id = str(uuid.uuid4())
        
        print(f"Email sent successfully to {request.to} with subject: {request.subject}")
        print(f"Gmail tool result: {result}")
        
        return SendEmailResponse(
            success=True,
            message=f"Email sent successfully to {request.to}",
            email_id=email_id
        )
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# User Details Endpoints

@app.post("/api/users/details", response_model=UserDetailsResponse)
async def get_user_details(request: UserSearchRequest, background_tasks: BackgroundTasks):
    """Get user details by email and name, with EXA search if not found"""
    try:
        email = request.email.lower().strip()
        name = request.name.strip() if request.name else None
        
        # Check if user exists in storage and force_refresh is False
        if not request.force_refresh and user_storage.user_exists(email, name):
            existing_user = user_storage.get_user_details(email)
            if existing_user:
                return UserDetailsResponse(
                    success=True,
                    user_details=existing_user,
                    message="User details retrieved from cache",
                    from_cache=True
                )
        
        # If not found or force_refresh is True, fetch from EXA in background
        if request.force_refresh or not user_storage.user_exists(email, name):
            background_tasks.add_task(fetch_user_details_background, email, name)
            
            return UserDetailsResponse(
                success=True,
                user_details=None,
                message="User details search initiated. Check back in a few moments.",
                from_cache=False
            )
        
        return UserDetailsResponse(
            success=False,
            user_details=None,
            message="User not found and search could not be initiated",
            from_cache=False
        )
        
    except Exception as e:
        print(f"Error in get_user_details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user details: {str(e)}")

@app.get("/api/users/{email}", response_model=UserDetailsResponse)
async def get_user_by_email(email: str):
    """Get user details by email from storage"""
    try:
        email = email.lower().strip()
        user_details = user_storage.get_user_details(email)
        
        if user_details:
            return UserDetailsResponse(
                success=True,
                user_details=user_details,
                message="User details found",
                from_cache=True
            )
        else:
            return UserDetailsResponse(
                success=False,
                user_details=None,
                message="User not found in storage",
                from_cache=False
            )
            
    except Exception as e:
        print(f"Error getting user by email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@app.get("/api/users/search/{query}", response_model=UserSearchResponse)
async def search_users(query: str, limit: int = 10):
    """Search users by name, email, or company"""
    try:
        users = user_storage.search_users(query)
        limited_users = users[:limit]
        
        return UserSearchResponse(
            success=True,
            users=limited_users,
            total_count=len(users),
            message=f"Found {len(users)} users matching '{query}'"
        )
        
    except Exception as e:
        print(f"Error searching users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search users: {str(e)}")

@app.get("/api/users", response_model=UserSearchResponse)
async def get_all_users(limit: int = 50):
    """Get all stored users"""
    try:
        users = user_storage.get_all_users()
        limited_users = users[:limit]
        
        return UserSearchResponse(
            success=True,
            users=limited_users,
            total_count=len(users),
            message=f"Retrieved {len(limited_users)} users"
        )
        
    except Exception as e:
        print(f"Error getting all users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@app.delete("/api/users/{email}")
async def delete_user(email: str):
    """Delete user from storage"""
    try:
        email = email.lower().strip()
        success = user_storage.delete_user(email)
        
        if success:
            return {"success": True, "message": f"User {email} deleted successfully"}
        else:
            return {"success": False, "message": f"User {email} not found"}
            
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

# Background task for fetching user details
async def fetch_user_details_background(email: str, name: str = None):
    """Background task to fetch user details using EXA"""
    try:
        print(f"Starting background user details fetch for: {email}, {name}")
        user_details = user_details_crew.fetch_user_details(email, name, force_refresh=True)
        print(f"User details fetched and stored for: {email}")
    except Exception as e:
        print(f"Error in background user details fetch: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if required environment variables are set
    required_env_vars = ["MY_EMAIL", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
    
    # Check for credentials file
    credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if not os.path.exists(credentials_path):
        print(f"Warning: Gmail credentials file not found at {credentials_path}")
        print("Please ensure you have set up Gmail API credentials")
    
    print("Starting Email Auto Responder API server...")
    print("API will be available at: http://localhost:8002")
    print("API documentation at: http://localhost:8002/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)