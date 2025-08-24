const API_BASE_URL = 'http://localhost:8002'

export interface ApiEmail {
  id: string
  threadId: string
  subject: string
  sender: string
  recipient: string
  body: string
  snippet: string
  timestamp: string
  labels: string[]
  is_read: boolean
  is_important: boolean
  drafts?: Array<{
    draft_id: string
    content: string
    created_at: string
    status: string
    response_type: string
  }>
}

export interface EmailBatch {
  emails: ApiEmail[]
  total_count: number
  has_more: boolean
  next_page_token?: string
}

export interface EmailSearchQuery {
  query: string
  limit?: number
  include_body?: boolean
  start_date?: string
  end_date?: string
}

export interface EmailAnalysis {
  total_emails: number
  unread_count: number
  important_count: number
  unique_senders: number
  unique_domains: number
  top_senders: Array<{ sender: string; count: number }>
  top_domains: Array<{ domain: string; count: number }>
  average_snippet_length: number
}

export interface GmailLabel {
  id: string
  name: string
}

export interface DraftRequest {
  to: string
  subject: string
  message: string
}

export interface DraftResponse {
  success: boolean
  message: string
  draft_id?: string
}

export interface AgentDraftRequest {
  emails: Array<{
    id: string
    threadId: string
    snippet: string
    sender: string
  }>
}

export interface SendEmailRequest {
  to: string
  cc?: string
  bcc?: string
  subject: string
  content: string
  from_email?: string
  reply_to_id?: string
}

export interface SendEmailResponse {
  success: boolean
  message: string
  email_id?: string
}

export interface UserDetails {
  email: string
  name?: string
  company?: string
  role?: string
  bio?: string
  linkedin_url?: string
  twitter_url?: string
  website?: string
  location?: string
  industry?: string
  created_at: string
  updated_at: string
  source: string
}

export interface UserSearchRequest {
  email: string
  name?: string
  force_refresh?: boolean
}

export interface UserDetailsResponse {
  success: boolean
  user_details?: UserDetails
  message: string
  from_cache: boolean
}

export interface UserSearchResponse {
  success: boolean
  users: UserDetails[]
  total_count: number
  message: string
}

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new ApiError(`API request failed: ${response.statusText}`, response.status)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new ApiError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

export const emailApi = {
  // Fetch emails with filtering
  async getEmails(query = 'after:newer_than:1d', limit = 50, includeBody = false): Promise<EmailBatch> {
    const params = new URLSearchParams({
      query,
      limit: limit.toString(),
      include_body: includeBody.toString(),
    })
    return fetchApi<EmailBatch>(`/api/emails?${params}`)
  },

  // Get unread emails
  async getUnreadEmails(limit = 50): Promise<EmailBatch> {
    const params = new URLSearchParams({ limit: limit.toString() })
    return fetchApi<EmailBatch>(`/api/emails/unread?${params}`)
  },

  // Get important emails
  async getImportantEmails(limit = 50): Promise<EmailBatch> {
    const params = new URLSearchParams({ limit: limit.toString() })
    return fetchApi<EmailBatch>(`/api/emails/important?${params}`)
  },

  // Get emails from specific sender
  async getEmailsBySender(senderEmail: string, limit = 50): Promise<EmailBatch> {
    const params = new URLSearchParams({ limit: limit.toString() })
    return fetchApi<EmailBatch>(`/api/emails/sender/${encodeURIComponent(senderEmail)}?${params}`)
  },

  // Get emails by date range
  async getEmailsByDateRange(startDate: string, endDate?: string, limit = 50): Promise<EmailBatch> {
    const params = new URLSearchParams({
      start_date: startDate,
      limit: limit.toString(),
    })
    if (endDate) {
      params.append('end_date', endDate)
    }
    return fetchApi<EmailBatch>(`/api/emails/date-range?${params}`)
  },

  // Get specific email details
  async getEmailDetails(emailId: string): Promise<ApiEmail> {
    return fetchApi<ApiEmail>(`/api/emails/${emailId}`)
  },

  // Advanced email search
  async searchEmails(searchQuery: EmailSearchQuery): Promise<EmailBatch> {
    return fetchApi<EmailBatch>('/api/emails/search', {
      method: 'POST',
      body: JSON.stringify(searchQuery),
    })
  },

  // Get email analytics
  async getEmailAnalysis(): Promise<EmailAnalysis> {
    return fetchApi<EmailAnalysis>('/api/emails/analysis')
  },

  // Get Gmail labels
  async getGmailLabels(): Promise<GmailLabel[]> {
    return fetchApi<GmailLabel[]>('/gmail/labels')
  },

  async healthCheck(): Promise<{ status: string; service: string }> {
    return fetchApi<{ status: string; service: string }>('/health')
  },

  async createDraft(draftRequest: DraftRequest): Promise<DraftResponse> {
    return fetchApi<DraftResponse>('/emails/draft', {
      method: 'POST',
      body: JSON.stringify(draftRequest),
    })
  },

  async createAgentDraft(agentDraftRequest: AgentDraftRequest): Promise<DraftResponse> {
    return fetchApi<DraftResponse>('/api/emails/agent-draft', {
      method: 'POST',
      body: JSON.stringify(agentDraftRequest),
    })
  },

  async sendEmail(emailData: SendEmailRequest): Promise<SendEmailResponse> {
    return fetchApi<SendEmailResponse>('/api/emails/send', {
      method: 'POST',
      body: JSON.stringify(emailData),
    })
  },

  async fetchEmailsWithAgent(): Promise<{ success: boolean; message: string; new_emails_count: number; total_checked: number }> {
    return fetchApi('/api/emails/fetch', {
      method: 'POST',
    })
  },

  async getDrafts(): Promise<{ success: boolean; drafts: any[]; total_count: number }> {
    return fetchApi('/api/drafts')
  },
}

export const userApi = {
  async getUserDetails(request: UserSearchRequest): Promise<UserDetailsResponse> {
    return fetchApi('/api/users/details', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  async getUserByEmail(email: string): Promise<UserDetailsResponse> {
    return fetchApi(`/api/users/${encodeURIComponent(email)}`)
  },

  async searchUsers(query: string, limit = 10): Promise<UserSearchResponse> {
    return fetchApi(`/api/users/search/${encodeURIComponent(query)}?limit=${limit}`)
  },

  async getAllUsers(limit = 50): Promise<UserSearchResponse> {
    return fetchApi(`/api/users?limit=${limit}`)
  },

  async deleteUser(email: string): Promise<{ success: boolean; message: string }> {
    return fetchApi(`/api/users/${encodeURIComponent(email)}`, {
      method: 'DELETE',
    })
  },
}

export { ApiError }
