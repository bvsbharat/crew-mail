"use client"

import { useState, useRef, useEffect } from "react"
import { Archive, Trash2, Clock, Menu, MoreHorizontal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { Input } from "@/components/ui/input"
import type { Email, EmailFolder } from "@/types/email"
import { formatDistanceToNow } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { AvatarWithLogo } from "@/components/avatar-with-logo"

interface EmailListProps {
  emails: Email[]
  selectedEmail: Email | null
  selectedFolder: EmailFolder
  onSelectEmail: (email: Email) => void
  onToggleSidebar: () => void
  onArchiveEmail: (id: string) => void
  onDeleteEmail: (id: string) => void
  onSnoozeEmail: (id: string, snoozeUntil: Date) => void
  loading?: boolean
  error?: string | null
  onToggleSelect?: (email: Email) => void
  selectedEmails?: Email[]
}

export default function EmailList({
  emails,
  selectedEmail,
  selectedFolder,
  onSelectEmail,
  onToggleSidebar,
  onArchiveEmail,
  onDeleteEmail,
  onSnoozeEmail,
  loading = false,
  error = null,
  onToggleSelect,
  selectedEmails = [],
}: EmailListProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [sortBy, setSortBy] = useState<'date' | 'sender'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Filter emails based on search query
  const filteredEmails = emails.filter(
    (email) =>
      email.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      email.sender.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      email.content.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  // Sort emails based on selected criteria
  const sortedEmails = [...filteredEmails].sort((a, b) => {
    if (sortBy === 'date') {
      const dateA = new Date(a.date).getTime()
      const dateB = new Date(b.date).getTime()
      return sortOrder === 'desc' ? dateB - dateA : dateA - dateB
    } else if (sortBy === 'sender') {
      const nameA = a.sender.name.toLowerCase()
      const nameB = b.sender.name.toLowerCase()
      return sortOrder === 'desc' ? nameB.localeCompare(nameA) : nameA.localeCompare(nameB)
    }
    return 0
  })

  const handleSortChange = (newSortBy: 'date' | 'sender') => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')
    } else {
      setSortBy(newSortBy)
      setSortOrder('desc')
    }
  }

  // Get folder name for display
  const getFolderName = () => {
    switch (selectedFolder) {
      case "unified":
        return "Unified Inbox"
      case "unread":
        return "Unread"
      case "flagged":
        return "Flagged"
      case "snoozed":
        return "Snoozed"
      case "archived":
        return "Archived"
      case "trash":
        return "Trash"
      default:
        return selectedFolder
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 flex items-center justify-between border-b border-border/50">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={onToggleSidebar} className="md:hidden">
            <Menu className="h-5 w-5" />
          </Button>
          <h2 className="text-lg font-medium">{getFolderName()}</h2>
        </div>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Mark all as read</DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => handleSortChange('date')}
                className={sortBy === 'date' ? 'bg-accent' : ''}
              >
                Sort by date {sortBy === 'date' && (sortOrder === 'desc' ? '↓' : '↑')}
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => handleSortChange('sender')}
                className={sortBy === 'sender' ? 'bg-accent' : ''}
              >
                Sort by sender {sortBy === 'sender' && (sortOrder === 'desc' ? '↓' : '↑')}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <div className="p-2">
        <Input
          placeholder="Search emails..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-background/80"
        />
      </div>

      <ScrollArea className="flex-1">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
            <p>Loading emails...</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <div className="text-red-500 mb-2">⚠️</div>
            <p className="text-red-500 text-center px-4">{error}</p>
            <p className="text-sm mt-2">Check that the backend API is running</p>
          </div>
        ) : sortedEmails.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <p>No emails found</p>
          </div>
        ) : (
          <div className="divide-y divide-border/50">
            {sortedEmails.map((email) => (
              <EmailListItem
                key={email.id}
                email={email}
                isSelected={selectedEmail?.id === email.id}
                onSelect={() => onSelectEmail(email)}
                onArchive={() => onArchiveEmail(email.id)}
                onDelete={() => onDeleteEmail(email.id)}
                onSnooze={onSnoozeEmail}
                onToggleSelect={onToggleSelect}
                isSelectedForDraft={selectedEmails.some(e => e.id === email.id)}
                showCheckbox={!!onToggleSelect}
              />
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  )
}

interface EmailListItemProps {
  email: Email
  isSelected: boolean
  onSelect: () => void
  onArchive: () => void
  onDelete: () => void
  onSnooze: (id: string, snoozeUntil: Date) => void
  onToggleSelect?: (email: Email) => void
  isSelectedForDraft?: boolean
  showCheckbox?: boolean
}

function EmailListItem({ email, isSelected, onSelect, onArchive, onDelete, onSnooze, onToggleSelect, isSelectedForDraft = false, showCheckbox = false }: EmailListItemProps) {
  const [isHovered, setIsHovered] = useState(false)
  const itemRef = useRef<HTMLDivElement>(null)

  // Scroll into view when selected
  useEffect(() => {
    if (isSelected && itemRef.current) {
      itemRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" })
    }
  }, [isSelected])

  // Helper function to determine which badges to show
  const getBadges = () => {
    const badges = []

    if (email.account === "work") {
      badges.push({ label: "Work", variant: "default" })
    }

    if (email.account === "personal") {
      badges.push({ label: "Personal", variant: "secondary" })
    }

    if (email.flagged) {
      badges.push({ label: "Important", variant: "destructive" })
    }

    if (email.attachments && email.attachments.length > 0) {
      badges.push({
        label: `${email.attachments.length} Attachment${email.attachments.length > 1 ? "s" : ""}`,
        variant: "outline",
      })
    }

    return badges
  }

  return (
    <div
      ref={itemRef}
      className={`p-3 cursor-pointer relative flex items-center gap-3 ${
        isSelected
          ? "bg-primary/10 border-l-4 border-primary shadow-sm"
          : isHovered
            ? "bg-muted/50 border-l-4 border-transparent"
            : "border-l-4 border-transparent"
      } ${!email.read ? "font-medium" : ""} ${
        isSelectedForDraft ? "bg-blue-50 dark:bg-blue-950/20" : ""
      }`}
      onClick={(e) => {
        // Allow email selection even when checkboxes are shown
        onSelect()
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {showCheckbox && (
        <input
          type="checkbox"
          checked={isSelectedForDraft}
          onChange={() => onToggleSelect?.(email)}
          className="mr-2 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          onClick={(e) => e.stopPropagation()}
        />
      )}
      <AvatarWithLogo sender={email.sender} />

      <div className="flex-1 min-w-0">
        {/* Combined subject and sender name on one line */}
        <div className="flex justify-between items-center mb-1">
          <div className="truncate text-sm">
            {email.subject} <span className="text-muted-foreground">from {email.sender.name}</span>
          </div>
          <div className="text-xs text-muted-foreground whitespace-nowrap ml-2">
            {formatDistanceToNow(new Date(email.date))}
          </div>
        </div>

        {/* Preview of email content */}
        <div className="text-xs text-muted-foreground truncate mb-2">{email.content.substring(0, 100)}...</div>

        {/* Badges for email categories */}
        <div className="flex flex-wrap gap-1.5">
          {getBadges().map((badge, index) => (
            <Badge key={index} variant={badge.variant as any} className="text-xs px-1.5 py-0">
              {badge.label}
            </Badge>
          ))}
          {!email.read && (
            <Badge variant="secondary" className="bg-blue-500 text-white hover:bg-blue-500/90 text-xs px-1.5 py-0">
              New
            </Badge>
          )}
          {email.drafts && email.drafts.length > 0 && (
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 hover:bg-green-100 text-xs px-1.5 py-0">
              {email.drafts.length} Draft Response{email.drafts.length > 1 ? 's' : ''}
            </Badge>
          )}
        </div>

        {/* Draft responses preview */}
        {email.drafts && email.drafts.length > 0 && (
          <div className="mt-2 p-2 bg-green-50 dark:bg-green-950/20 rounded-md border border-green-200 dark:border-green-800">
            <div className="text-xs font-medium text-green-800 dark:text-green-200 mb-1">
              AI Draft Response:
            </div>
            <div className="text-xs text-green-700 dark:text-green-300 truncate">
              {email.drafts[0].content.substring(0, 120)}...
            </div>
          </div>
        )}
      </div>

      {/* Action buttons - positioned absolutely to not affect row height */}
      {isHovered && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex gap-1 bg-muted/80 backdrop-blur-sm px-1 py-0.5 rounded-md">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={(e) => {
              e.stopPropagation()
              onArchive()
            }}
          >
            <Archive className="h-4 w-4" />
          </Button>

          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={(e) => e.stopPropagation()}>
                <Clock className="h-4 w-4" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <div className="p-2">
                <div className="font-medium mb-2">Snooze until</div>
                <div className="space-y-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start"
                    onClick={(e) => {
                      e.stopPropagation()
                      const tomorrow = new Date()
                      tomorrow.setDate(tomorrow.getDate() + 1)
                      tomorrow.setHours(9, 0, 0, 0)
                      onSnooze(email.id, tomorrow)
                    }}
                  >
                    Tomorrow morning
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start"
                    onClick={(e) => {
                      e.stopPropagation()
                      const nextWeek = new Date()
                      nextWeek.setDate(nextWeek.getDate() + 7)
                      nextWeek.setHours(9, 0, 0, 0)
                      onSnooze(email.id, nextWeek)
                    }}
                  >
                    Next week
                  </Button>
                </div>
                <Calendar
                  mode="single"
                  selected={undefined}
                  onSelect={(date) => {
                    if (date) {
                      onSnooze(email.id, date)
                    }
                  }}
                  className="mt-2"
                />
              </div>
            </PopoverContent>
          </Popover>

          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={(e) => {
              e.stopPropagation()
              onDelete()
            }}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  )
}
