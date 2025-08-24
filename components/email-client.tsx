"use client"

import { useState, useEffect, useMemo, useCallback } from "react"
import Sidebar from "@/components/sidebar"
import EmailList from "@/components/email-list"
import EmailDetail from "@/components/email-detail"
import { AgentDraftGenerator } from "@/components/agent-draft-generator"
import type { Email, EmailAccount, EmailFolder } from "@/types/email"
import { mockAccounts } from "@/lib/mock-data"
import { useEmailApi } from "@/hooks/use-email-api"
import { useMobile } from "@/hooks/use-mobile"
import { useToast } from "@/hooks/use-toast"
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from "@/components/ui/resizable"

export default function EmailClient() {
  const [selectedFolder, setSelectedFolder] = useState<EmailFolder>("unified")
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null)
  const [selectedEmails, setSelectedEmails] = useState<Email[]>([])
  const [accounts, setAccounts] = useState<EmailAccount[]>(mockAccounts)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [detailOpen, setDetailOpen] = useState(false)
  const [showAgentDraft, setShowAgentDraft] = useState(false)
  const isMobile = useMobile()
  const { toast } = useToast()
  
  // Use the email API hook
  const { 
    emails, 
    loading, 
    error,
    sendEmail, 
    fetchEmails, 
    fetchEmailDetails,
    fetchEmailsWithAgent,
    getDrafts,
    setEmails,
    checkApiHealth 
  } = useEmailApi()

  // State for drafts
  const [drafts, setDrafts] = useState<any[]>([])

  // Filter emails based on selected folder
  const filteredEmails = useMemo(() => {
    if (selectedFolder === "drafts") {
      // Only show actual draft emails - return drafts array converted to email format
      return drafts.map((draft) => ({
        id: draft.draft_id || draft.id,
        subject: draft.subject || "Draft Response",
        sender: {
          name: "AI Assistant",
          email: "ai@assistant.com"
        },
        recipients: [],
        content: draft.content || "No content available",
        date: draft.created_at || new Date().toISOString(),
        read: true,
        flagged: false,
        snoozed: false,
        archived: false,
        deleted: false,
        account: "drafts",
        labels: ["draft"],
        categories: [],
        attachments: [],
        drafts: []
      }))
    }

    // For all other folders, filter regular emails (exclude drafts folder completely)
    return emails.filter((email) => {
      if (email.deleted) return false
      if (email.snoozed) return selectedFolder === "snoozed"
      if (email.archived) return selectedFolder === "archived"

      if (selectedFolder === "unified") return !email.archived && !email.snoozed
      if (selectedFolder === "unread") return !email.read && !email.archived && !email.snoozed
      if (selectedFolder === "flagged") return email.flagged && !email.archived && !email.snoozed

      return email.account === selectedFolder && !email.archived && !email.snoozed
    })
  }, [emails, selectedFolder, drafts])

  // Initialize API connection and fetch emails
  useEffect(() => {
    const initializeApp = async () => {
      const isHealthy = await checkApiHealth()
      if (isHealthy) {
        fetchEmails(selectedFolder)
      }
    }
    initializeApp()
  }, [checkApiHealth, fetchEmails, selectedFolder])

  // Fetch drafts when drafts folder is selected
  useEffect(() => {
    const fetchDraftsData = async () => {
      if (selectedFolder === "drafts") {
        try {
          const draftsData = await getDrafts()
          setDrafts(draftsData)
        } catch (error) {
          console.error('Failed to fetch drafts:', error)
          toast({
            title: "Error",
            description: "Failed to fetch drafts",
            variant: "destructive",
          })
        }
      }
    }

    fetchDraftsData()
  }, [selectedFolder, getDrafts])

  // Fetch emails when folder changes (except for drafts)
  useEffect(() => {
    if (emails.length > 0 && selectedFolder !== "drafts") { // Only refetch if we already have emails loaded and not drafts
      fetchEmails(selectedFolder)
    }
  }, [selectedFolder, fetchEmails])

  // Close sidebar on mobile by default
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false)
    } else {
      setSidebarOpen(true)
    }
  }, [isMobile])

  // Close detail view when no email is selected
  useEffect(() => {
    if (!selectedEmail) {
      setDetailOpen(false)
    }
  }, [selectedEmail])

  // Handle email selection
  const handleEmailSelect = useCallback(async (email: Email) => {
    setSelectedEmail(email)

    // Mark as read locally
    setEmails(prevEmails => prevEmails.map((e) => (e.id === email.id ? { ...e, read: true } : e)))

    // Always fetch full email details to ensure we have latest drafts
    const fullEmail = await fetchEmailDetails(email.id)
    if (fullEmail) {
      setSelectedEmail(fullEmail)
      setEmails(prevEmails => prevEmails.map((e) => (e.id === email.id ? { ...e, ...fullEmail } : e)))
    }

    // Open detail view on mobile
    if (isMobile) {
      setDetailOpen(true)
    }
  }, [fetchEmailDetails, isMobile])

  // Handle email snooze
  const handleSnoozeEmail = (emailId: string, snoozeUntil: Date) => {
    setEmails(emails.map((email) => (email.id === emailId ? { ...email, snoozed: true, snoozeUntil } : email)))
  }

  // Handle email archive
  const handleArchiveEmail = (emailId: string) => {
    setEmails(prevEmails => prevEmails.map((email) => (email.id === emailId ? { ...email, archived: true } : email)))

    if (selectedEmail?.id === emailId) {
      setSelectedEmail(null)
    }
  }

  // Handle email delete
  const handleDeleteEmail = (emailId: string) => {
    setEmails(prevEmails => prevEmails.map((email) => (email.id === emailId ? { ...email, deleted: true } : email)))

    if (selectedEmail?.id === emailId) {
      setSelectedEmail(null)
    }
  }

  // Handle sending email
  const handleSendEmail = async (email: any) => {
    try {
      const emailData = {
        to: email.to,
        cc: email.cc,
        bcc: email.bcc,
        subject: email.subject,
        content: email.content,
        from_email: email.from,
        reply_to_id: email.replyToId
      }
      
      const success = await sendEmail(emailData)
      if (!success) {
        toast({
          title: "Error",
          description: "Failed to send email. Please try again.",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error('Error sending email:', error)
      toast({
        title: "Error",
        description: "Failed to send email. Please try again.",
        variant: "destructive",
      })
    }
  }

  // Handle email selection for agent draft
  const handleEmailToggleSelect = (email: Email) => {
    setSelectedEmails(prev => {
      const isSelected = prev.some(e => e.id === email.id)
      if (isSelected) {
        return prev.filter(e => e.id !== email.id)
      } else {
        return [...prev, email]
      }
    })
  }

  // Handle agent draft generation
  const handleDraftGenerated = async () => {
    setSelectedEmails([])
    
    // Refresh drafts if currently viewing drafts folder
    if (selectedFolder === "drafts") {
      try {
        const draftsData = await getDrafts()
        setDrafts(draftsData)
      } catch (error) {
        console.error('Failed to refresh drafts:', error)
      }
    }
    
    toast({
      title: "Success",
      description: "Draft responses have been generated and saved to your drafts.",
    })
  }

  // Toggle agent draft panel
  const handleToggleAgentDraft = () => {
    setShowAgentDraft(!showAgentDraft)
    if (!showAgentDraft) {
      setSelectedEmails([])
    }
  }

  // Handle fetching emails with CrewAI agent
  const handleFetchEmailsWithAgent = async () => {
    await fetchEmailsWithAgent()
  }

  // Select first email by default
  useEffect(() => {
    if (emails.length > 0 && !selectedEmail && !loading) {
      const firstVisibleEmail = filteredEmails[0]
      if (firstVisibleEmail) {
        handleEmailSelect(firstVisibleEmail)
      }
    }
  }, [emails, filteredEmails, selectedEmail, loading, handleEmailSelect])

  return (
    <div className="flex h-screen w-full">
      {/* Sidebar */}
      <div
        className={`${sidebarOpen ? "block" : "hidden"} md:block border-r border-border/50 bg-background/60 backdrop-blur-md`}
      >
        <Sidebar
          accounts={accounts}
          selectedFolder={selectedFolder}
          onSelectFolder={setSelectedFolder}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          onSendEmail={handleSendEmail}
          onToggleAgentDraft={handleToggleAgentDraft}
          onFetchEmailsWithAgent={handleFetchEmailsWithAgent}
          showAgentDraft={showAgentDraft}
        />
      </div>

      {/* Main Content with Resizable Panels */}
      {isMobile ? (
        // Mobile view - show either list or detail
        <div className="flex-1">
          {detailOpen && selectedEmail ? (
            <EmailDetail
              email={selectedEmail}
              onClose={() => setDetailOpen(false)}
              onArchive={() => handleArchiveEmail(selectedEmail.id)}
              onDelete={() => handleDeleteEmail(selectedEmail.id)}
              onSnooze={handleSnoozeEmail}
            />
          ) : (
            <EmailList
              emails={filteredEmails}
              selectedEmail={selectedEmail}
              onSelectEmail={handleEmailSelect}
              onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
              onArchiveEmail={handleArchiveEmail}
              onDeleteEmail={handleDeleteEmail}
              onSnoozeEmail={handleSnoozeEmail}
              selectedFolder={selectedFolder}
              loading={loading}
              error={error}
            />
          )}
        </div>
      ) : (
        // Desktop view - resizable panels
        <ResizablePanelGroup direction="horizontal" className="flex-1">
          <ResizablePanel defaultSize={showAgentDraft ? 25 : 30} minSize={20}>
            <EmailList
              emails={filteredEmails}
              selectedEmail={selectedEmail}
              onSelectEmail={handleEmailSelect}
              onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
              onArchiveEmail={handleArchiveEmail}
              onDeleteEmail={handleDeleteEmail}
              onSnoozeEmail={handleSnoozeEmail}
              selectedFolder={selectedFolder}
              loading={loading}
              error={error}
              onToggleSelect={handleEmailToggleSelect}
              selectedEmails={selectedEmails}
            />
          </ResizablePanel>
          <ResizableHandle />
          {showAgentDraft && (
            <>
              <ResizablePanel defaultSize={25} minSize={20}>
                <AgentDraftGenerator
                  selectedEmails={selectedEmails}
                  onDraftGenerated={handleDraftGenerated}
                  onClose={handleToggleAgentDraft}
                />
              </ResizablePanel>
              <ResizableHandle />
            </>
          )}
          <ResizablePanel defaultSize={showAgentDraft ? 50 : 70}>
            {selectedEmail ? (
              <EmailDetail
                email={selectedEmail}
                onClose={() => setSelectedEmail(null)}
                onArchive={() => handleArchiveEmail(selectedEmail.id)}
                onDelete={() => handleDeleteEmail(selectedEmail.id)}
                onSnooze={handleSnoozeEmail}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                Select an email to view
              </div>
            )}
          </ResizablePanel>
        </ResizablePanelGroup>
      )}
    </div>
  )
}
