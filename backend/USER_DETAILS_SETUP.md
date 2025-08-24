# User Details Fetching Agent Setup

## Overview

The user details fetching agent automatically researches and stores professional information about email senders using EXA search API. When users click on a sender's avatar in the email interface, detailed professional information is displayed.

## Features

- **Automatic User Research**: Fetches user details when new email senders are encountered
- **EXA Integration**: Uses EXA API for professional information search
- **File System Storage**: Stores user data locally with uniqueness checks
- **Background Processing**: Non-blocking user details fetching
- **RESTful API**: Complete API endpoints for user management

## Architecture

```
User Details System
├── UserDetailsCrew (CrewAI)
│   ├── user_research_agent (EXA search)
│   └── data_validation_agent (data cleaning)
├── UserStorage (File system)
│   ├── users.json (index)
│   ├── profiles/ (detailed profiles)
│   └── cache/ (temporary data)
└── API Endpoints
    ├── POST /api/users/details
    ├── GET /api/users/{email}
    ├── GET /api/users/search/{query}
    └── DELETE /api/users/{email}
```

## Setup Instructions

### 1. Environment Variables

Add to your `.env` file:

```bash
# Required for EXA search
EXA_API_KEY=your_exa_api_key_here

# Existing required variables
OPENAI_API_KEY=your_openai_api_key
MY_EMAIL=your_email@domain.com
```

### 2. Get EXA API Key

1. Visit [exa.ai](https://exa.ai)
2. Sign up for an account
3. Get your API key from the dashboard
4. Add it to your `.env` file

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Storage Directory

The system automatically creates storage directories:

```
backend/storage/user_details/
├── users.json          # Main user index
├── profiles/           # Individual user profiles
└── cache/             # Temporary search results
```

## API Endpoints

### Fetch User Details
```bash
POST /api/users/details
Content-Type: application/json

{
  "email": "john@company.com",
  "name": "John Smith",
  "force_refresh": false
}
```

### Get User by Email
```bash
GET /api/users/john@company.com
```

### Search Users
```bash
GET /api/users/search/john
GET /api/users/search/company
```

### Get All Users
```bash
GET /api/users?limit=50
```

### Delete User
```bash
DELETE /api/users/john@company.com
```

## Integration with Email Flow

The system automatically:

1. **Email Processing**: When emails are fetched, sender details are extracted
2. **Uniqueness Check**: Checks if user already exists in storage
3. **Background Fetch**: If new user, triggers EXA search in background
4. **Storage**: Saves user details to file system
5. **Frontend Access**: User details available when clicking user avatar

## User Data Structure

```json
{
  "email": "john@company.com",
  "name": "John Smith",
  "company": "Tech Corp",
  "role": "Senior Developer",
  "bio": "Experienced software developer...",
  "linkedin_url": "https://linkedin.com/in/johnsmith",
  "twitter_url": "https://twitter.com/johnsmith",
  "website": "https://johnsmith.dev",
  "location": "San Francisco, CA",
  "industry": "Technology",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "source": "exa"
}
```

## Frontend Integration

When user clicks on email sender avatar:

1. Frontend calls `GET /api/users/{email}`
2. If user exists, display details immediately
3. If not found, call `POST /api/users/details` to trigger search
4. Show loading state and poll for results

## Troubleshooting

### Common Issues

1. **EXA API Key Missing**
   - Error: "EXA_API_KEY not found in environment variables"
   - Solution: Add EXA_API_KEY to your .env file

2. **Storage Permissions**
   - Error: Permission denied creating storage directories
   - Solution: Ensure write permissions for backend/storage/

3. **CrewAI Configuration**
   - Error: Agent configuration not found
   - Solution: Ensure config/agents.yaml and config/tasks.yaml exist

### Debug Mode

Enable debug logging by setting:
```bash
export CREW_DEBUG=true
```

## Performance Considerations

- **Caching**: User details are cached locally to avoid repeated API calls
- **Background Processing**: EXA searches run in background to avoid blocking
- **Rate Limiting**: Respects EXA API rate limits
- **Uniqueness**: Prevents duplicate searches for same user

## Security

- **API Keys**: Store securely in environment variables
- **Data Privacy**: Only searches publicly available professional information
- **Local Storage**: User data stored locally, not transmitted to third parties
- **Email Validation**: Validates email formats before processing
