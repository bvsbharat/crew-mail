import { useState, useEffect, useCallback } from 'react'
import { emailApi, type EmailBatch, type ApiEmail, type EmailAnalysis, type DraftRequest, type AgentDraftRequest, type SendEmailRequest, ApiError } from '@/lib/api'
import { transformApiEmailToEmail } from '@/lib/email-utils'
import type { Email, EmailFolder } from '@/types/email'
import { useToast } from '@/hooks/use-toast'

export function useEmailApi() {
  const [emails, setEmails] = useState<Email[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<EmailAnalysis | null>(null)
  const { toast } = useToast()

  const handleApiError = useCallback((error: unknown, action: string) => {
    const message = error instanceof ApiError 
      ? `Failed to ${action}: ${error.message}`
      : `Failed to ${action}: Unknown error`
    
    setError(message)
    toast({
      title: "Error",
      description: message,
      variant: "destructive",
    })
  }, [toast])

  const fetchEmails = useCallback(async (folder: EmailFolder = 'unified', limit = 50) => {
    setLoading(true)
    setError(null)

    try {
      let batch: EmailBatch

      switch (folder) {
        case 'unread':
          batch = await emailApi.getUnreadEmails(limit)
          break
        case 'flagged':
          batch = await emailApi.getImportantEmails(limit)
          break
        case 'unified':
        default:
          batch = await emailApi.getEmails('after:newer_than:7d', limit, false)
          break
      }

      console.log('API Response:', batch)
      console.log('Raw emails count:', batch.emails.length)
      
      const transformedEmails = batch.emails.map(transformApiEmailToEmail)
      console.log('Transformed emails:', transformedEmails)
      console.log('Transformed emails count:', transformedEmails.length)
      
      setEmails(transformedEmails)
    } catch (error) {
      console.error('Error fetching emails:', error)
      handleApiError(error, 'fetch emails')
    } finally {
      setLoading(false)
    }
  }, [handleApiError])

  const fetchEmailDetails = useCallback(async (emailId: string): Promise<Email | null> => {
    try {
      const apiEmail = await emailApi.getEmailDetails(emailId)
      return transformApiEmailToEmail(apiEmail)
    } catch (error) {
      handleApiError(error, 'fetch email details')
      return null
    }
  }, [handleApiError])

  const searchEmails = useCallback(async (query: string, limit = 50) => {
    setLoading(true)
    setError(null)

    try {
      const batch = await emailApi.searchEmails({ query, limit, include_body: false })
      const transformedEmails = batch.emails.map(transformApiEmailToEmail)
      setEmails(transformedEmails)
    } catch (error) {
      handleApiError(error, 'search emails')
    } finally {
      setLoading(false)
    }
  }, [handleApiError])

  const fetchEmailsBySender = useCallback(async (senderEmail: string, limit = 50) => {
    setLoading(true)
    setError(null)

    try {
      const batch = await emailApi.getEmailsBySender(senderEmail, limit)
      const transformedEmails = batch.emails.map(transformApiEmailToEmail)
      setEmails(transformedEmails)
    } catch (error) {
      handleApiError(error, 'fetch emails by sender')
    } finally {
      setLoading(false)
    }
  }, [handleApiError])

  const fetchEmailsByDateRange = useCallback(async (startDate: string, endDate?: string, limit = 50) => {
    setLoading(true)
    setError(null)

    try {
      const batch = await emailApi.getEmailsByDateRange(startDate, endDate, limit)
      const transformedEmails = batch.emails.map(transformApiEmailToEmail)
      setEmails(transformedEmails)
    } catch (error) {
      handleApiError(error, 'fetch emails by date range')
    } finally {
      setLoading(false)
    }
  }, [handleApiError])

  const fetchEmailAnalysis = useCallback(async () => {
    try {
      const analysisData = await emailApi.getEmailAnalysis()
      setAnalysis(analysisData)
    } catch (error) {
      handleApiError(error, 'fetch email analysis')
    }
  }, [handleApiError])

  const checkApiHealth = useCallback(async (): Promise<boolean> => {
    try {
      await emailApi.healthCheck()
      return true
    } catch (error) {
      handleApiError(error, 'check API health')
      return false
    }
  }, [handleApiError])

  const createDraft = useCallback(async (draftRequest: DraftRequest): Promise<boolean> => {
    try {
      const response = await emailApi.createDraft(draftRequest)
      if (response.success) {
        toast({
          title: "Success",
          description: "Draft created successfully",
        })
        return true
      }
      return false
    } catch (error) {
      handleApiError(error, 'create draft')
      return false
    }
  }, [handleApiError, toast])

  const createAgentDraft = useCallback(async (emails: Email[]): Promise<boolean> => {
    try {
      const agentDraftRequest: AgentDraftRequest = {
        emails: emails.map(email => ({
          id: email.id,
          threadId: email.id, // Using email id as threadId fallback
          snippet: email.content.substring(0, 150) + '...', // Create snippet from content
          sender: email.sender.email
        }))
      }
      
      const response = await emailApi.createAgentDraft(agentDraftRequest)
      if (response.success) {
        toast({
          title: "Success",
          description: "Agent draft responses generated and saved successfully",
        })
        return true
      }
      return false
    } catch (error) {
      handleApiError(error, 'create agent draft')
      return false
    }
  }, [handleApiError, toast])

  const fetchEmailsWithAgent = useCallback(async (): Promise<boolean> => {
    setLoading(true)
    try {
      const response = await emailApi.fetchEmailsWithAgent()
      if (response.success) {
        toast({
          title: "Success",
          description: `${response.message}. Found ${response.new_emails_count} new emails.`,
        })
        // Refresh the email list after fetching
        await fetchEmails()
        return true
      }
      return false
    } catch (error) {
      handleApiError(error, 'fetch emails with CrewAI agent')
      return false
    } finally {
      setLoading(false)
    }
  }, [handleApiError, toast, fetchEmails])

  const getDrafts = useCallback(async () => {
    try {
      const response = await emailApi.getDrafts()
      if (response.success) {
        return response.drafts
      }
      return []
    } catch (error) {
      handleApiError(error, 'get drafts')
      return []
    }
  }, [handleApiError])

  const sendEmail = useCallback(async (emailData: SendEmailRequest): Promise<boolean> => {
    try {
      const response = await emailApi.sendEmail(emailData)
      if (response.success) {
        toast({
          title: "Success",
          description: response.message,
        })
        return true
      }
      return false
    } catch (error) {
      handleApiError(error, 'send email')
      return false
    }
  }, [handleApiError, toast])

  return {
    emails,
    loading,
    error,
    analysis,
    fetchEmails,
    fetchEmailDetails,
    searchEmails,
    fetchEmailsBySender,
    fetchEmailsByDateRange,
    fetchEmailAnalysis,
    checkApiHealth,
    createDraft,
    createAgentDraft,
    fetchEmailsWithAgent,
    getDrafts,
    sendEmail,
    setEmails,
    setError,
  }
}
