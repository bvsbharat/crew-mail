"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2, Bot, Mail } from "lucide-react"
import { useEmailApi } from "@/hooks/use-email-api"
import type { Email } from "@/types/email"

interface AgentDraftGeneratorProps {
  selectedEmails: Email[]
  onDraftGenerated?: () => void
  onClose?: () => void
}

export const AgentDraftGenerator = ({ selectedEmails, onDraftGenerated, onClose }: AgentDraftGeneratorProps) => {
  const [isGenerating, setIsGenerating] = useState(false)
  const { createAgentDraft } = useEmailApi()

  const handleGenerateDrafts = async () => {
    if (selectedEmails.length === 0) return

    setIsGenerating(true)
    try {
      const success = await createAgentDraft(selectedEmails)
      if (success && onDraftGenerated) {
        onDraftGenerated()
      }
    } finally {
      setIsGenerating(false)
    }
  }

  if (selectedEmails.length === 0) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            AI Draft Generator
          </CardTitle>
          <CardDescription>
            Select emails to generate AI-powered draft responses
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No emails selected</p>
            <p className="text-sm">Choose emails from your inbox to generate draft responses</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          AI Draft Generator
        </CardTitle>
        <CardDescription>
          Generate AI-powered draft responses for selected emails
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Selected Emails ({selectedEmails.length})</h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {selectedEmails.map((email) => (
              <div key={email.id} className="flex items-center justify-between p-2 bg-muted rounded-lg">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{email.subject}</p>
                  <p className="text-xs text-muted-foreground truncate">
                    From: {email.sender.name} ({email.sender.email})
                  </p>
                </div>
                <Badge variant={email.read ? "secondary" : "default"} className="ml-2">
                  {email.read ? "Read" : "Unread"}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-4 border-t">
          <Button 
            onClick={handleGenerateDrafts}
            disabled={isGenerating}
            className="w-full"
            size="lg"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Drafts...
              </>
            ) : (
              <>
                <Bot className="mr-2 h-4 w-4" />
                Generate AI Draft Responses
              </>
            )}
          </Button>
          
          <p className="text-xs text-muted-foreground mt-2 text-center">
            AI will analyze each email and create appropriate draft responses
          </p>
        </div>
      </CardContent>
    </Card>
  )
}