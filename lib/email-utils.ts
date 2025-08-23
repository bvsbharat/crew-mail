import type { Email, EmailSender, EmailCategory } from "@/types/email"
import type { ApiEmail } from "@/lib/api"

// Transform API email to frontend Email type
export function transformApiEmailToEmail(apiEmail: ApiEmail): Email {
  // Parse sender email to extract name and email
  const senderMatch = apiEmail.sender.match(/^(.*?)\s*<(.+)>$/) || [null, apiEmail.sender, apiEmail.sender]
  const senderName = senderMatch[1]?.trim() || apiEmail.sender.split('@')[0] || 'Unknown'
  const senderEmail = senderMatch[2]?.trim() || apiEmail.sender

  // Parse recipient email similarly
  const recipientMatch = apiEmail.recipient.match(/^(.*?)\s*<(.+)>$/) || [null, apiEmail.recipient, apiEmail.recipient]
  const recipientName = recipientMatch[1]?.trim() || apiEmail.recipient.split('@')[0] || 'You'
  const recipientEmail = recipientMatch[2]?.trim() || apiEmail.recipient

  const sender: EmailSender = {
    name: senderName,
    email: senderEmail,
    avatar: `/placeholder.svg?height=40&width=40&text=${senderName.charAt(0).toUpperCase()}`,
  }

  const recipient: EmailSender = {
    name: recipientName,
    email: recipientEmail,
  }

  return {
    id: apiEmail.id,
    subject: apiEmail.subject || 'No Subject',
    sender,
    recipients: [recipient],
    content: apiEmail.body || apiEmail.snippet || '',
    date: apiEmail.timestamp,
    read: apiEmail.is_read,
    flagged: apiEmail.is_important,
    snoozed: false,
    archived: false,
    deleted: false,
    labels: apiEmail.labels || [],
    account: 'primary', // Default to primary account
    categories: determineCategories(apiEmail),
    drafts: apiEmail.drafts || [],
  }
}

// Determine email categories based on content and labels
function determineCategories(apiEmail: ApiEmail): EmailCategory[] {
  const categories: EmailCategory[] = []
  
  // Check labels for category hints
  const labels = apiEmail.labels.map(label => label.toLowerCase())
  
  if (labels.includes('important') || labels.includes('starred')) {
    categories.push('work')
  }
  
  if (labels.includes('social') || labels.includes('updates')) {
    categories.push('social')
  }
  
  if (labels.includes('promotions') || labels.includes('category_promotions')) {
    categories.push('promotions')
  }
  
  // Analyze sender domain for category hints
  const senderDomain = apiEmail.sender.split('@')[1]?.toLowerCase()
  
  if (senderDomain) {
    if (senderDomain.includes('company') || senderDomain.includes('corp') || senderDomain.includes('business')) {
      categories.push('work')
    } else if (senderDomain.includes('gmail') || senderDomain.includes('yahoo') || senderDomain.includes('hotmail')) {
      categories.push('personal')
    }
  }
  
  // Default to personal if no other category determined
  if (categories.length === 0) {
    categories.push('personal')
  }
  
  return categories
}

// Format date for display
export function formatEmailDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
  
  if (diffInHours < 24) {
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
  } else if (diffInHours < 24 * 7) {
    return date.toLocaleDateString('en-US', { weekday: 'short' })
  } else {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })
  }
}

// Extract email address from formatted string
export function extractEmailAddress(emailString: string): string {
  const match = emailString.match(/<(.+)>/)
  return match ? match[1] : emailString
}

// Generate avatar placeholder
export function generateAvatarUrl(name: string, size = 40): string {
  const initial = name.charAt(0).toUpperCase()
  return `/placeholder.svg?height=${size}&width=${size}&text=${initial}`
}
