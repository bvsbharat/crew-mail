import type { Email, EmailAccount } from "@/types/email"

export const mockAccounts: EmailAccount[] = [
  {
    id: "personal",
    name: "Personal",
    email: "your.email@gmail.com",
    color: "#4285F4",
  },
  {
    id: "work",
    name: "Work",
    email: "your.name@company.com",
    color: "#EA4335",
  },
]

export const mockEmails: Email[] = [
  {
    id: "1",
    subject: "Weekly Team Update",
    sender: {
      name: "Alex Johnson",
      email: "alex.johnson@company.com",
      avatar: "/placeholder.svg?height=40&width=40",
      organization: {
        name: "Acme Corp",
        logo: "/placeholder.svg?height=20&width=20&text=AC",
        website: "https://acmecorp.example.com",
      },
      bio: "Product Manager with 8+ years of experience in SaaS products. Focused on user-centric design and agile methodologies.",
      role: "Senior Product Manager",
      location: "San Francisco, CA",
      timezone: "Pacific Time (PT)",
      socialLinks: [
        { platform: "LinkedIn", url: "#", username: "alexjohnson" },
        { platform: "Twitter", url: "#", username: "@alexj" },
        { platform: "GitHub", url: "#", username: "alexj-dev" },
      ],
      lastContacted: "2023-05-01",
      firstContacted: "2021-03-15",
      emailCount: 142,
    },
    recipients: [
      {
        name: "You",
        email: "your.name@company.com",
      },
    ],
    content: `Hi team,

Here's a summary of what we accomplished this week:

- Completed the user authentication feature
- Fixed 5 critical bugs in the payment system
- Started work on the new dashboard design

Let's discuss these items in our Monday meeting. Please come prepared with any questions or concerns.

Best regards,
Alex`,
    date: "2023-05-04T10:30:00",
    read: false,
    flagged: true,
    snoozed: false,
    archived: false,
    deleted: false,
    account: "work",
    categories: ["work", "updates"],
  },
  {
    id: "2",
    subject: "Vacation Plans",
    sender: {
      name: "Sarah Miller",
      email: "sarah.miller@gmail.com",
      avatar: "/placeholder.svg?height=40&width=40",
      bio: "Travel enthusiast, photographer, and foodie. Always planning the next adventure!",
      location: "New York, NY",
      socialLinks: [
        { platform: "Instagram", url: "#", username: "@sarahtravels" },
        { platform: "Pinterest", url: "#", username: "sarahmiller" },
      ],
      lastContacted: "2023-04-28",
      firstContacted: "2019-06-22",
      emailCount: 87,
    },
    recipients: [
      {
        name: "You",
        email: "your.email@gmail.com",
      },
    ],
    content: `Hey!

I've been looking at some options for our summer vacation. What do you think about these destinations:

1. Costa Rica - Great beaches and rainforests
2. Japan - Amazing food and culture
3. Italy - Beautiful cities and countryside

Let me know your thoughts. We should book soon to get the best prices.

Sarah`,
    date: "2023-05-03T15:45:00",
    read: true,
    flagged: false,
    snoozed: false,
    archived: false,
    deleted: false,
    account: "personal",
  },
  {
    id: "3",
    subject: "Invoice #1234",
    sender: {
      name: "Billing Department",
      email: "billing@service.com",
      avatar: "/placeholder.svg?height=40&width=40",
      organization: {
        name: "Cloud Services Inc",
        logo: "/placeholder.svg?height=20&width=20&text=CS",
        website: "https://cloudservices.example.com",
      },
      role: "Automated Billing System",
      lastContacted: "2023-04-02",
      firstContacted: "2022-01-10",
      emailCount: 16,
    },
    recipients: [
      {
        name: "You",
        email: "your.email@gmail.com",
      },
    ],
    content: `Dear Customer,

Your invoice #1234 for April 2023 is now available. The total amount due is $89.99.

Payment is due by May 15, 2023. You can view and pay your invoice by logging into your account.

Thank you for your business!

Billing Department`,
    date: "2023-05-02T09:15:00",
    read: true,
    flagged: false,
    snoozed: false,
    archived: false,
    deleted: false,
    attachments: [
      {
        name: "Invoice_1234.pdf",
        size: "156 KB",
        type: "application/pdf",
        url: "#",
      },
    ],
    account: "personal",
  },
  {
    id: "4",
    subject: "Project Deadline Extension",
    sender: {
      name: "Michael Chen",
      email: "michael.chen@company.com",
      avatar: "/placeholder.svg?height=40&width=40",
      organization: {
        name: "Acme Corp",
        logo: "/placeholder.svg?height=20&width=20&text=AC",
        website: "https://acmecorp.example.com",
      },
      bio: "Project Manager specializing in software development lifecycles and team coordination. Certified PMP and Scrum Master.",
      role: "Project Manager",
      location: "Seattle, WA",
      timezone: "Pacific Time (PT)",
      socialLinks: [
        { platform: "LinkedIn", url: "#", username: "michaelchen" },
        { platform: "Twitter", url: "#", username: "@mchen_pm" },
      ],
      lastContacted: "2023-04-29",
      firstContacted: "2021-11-05",
      emailCount: 98,
    },
    recipients: [
      {
        name: "You",
        email: "your.name@company.com",
      },
      {
        name: "Project Team",
        email: "project-team@company.com",
      },
    ],
    content: `Hello everyone,

I'm writing to inform you that the deadline for the current project phase has been extended by one week. The new deadline is May 20, 2023.

This extension is due to the additional requirements that were added last week. Please use this extra time to ensure all features are properly implemented and tested.

If you have any questions, feel free to reach out.

Best regards,
Michael Chen
Project Manager`,
    date: "2023-05-01T14:20:00",
    read: false,
    flagged: true,
    snoozed: false,
    archived: false,
    deleted: false,
    account: "work",
  },
  {
    id: "5",
    subject: "Dinner this weekend?",
    sender: {
      name: "Emily Davis",
      email: "emily.davis@gmail.com",
      avatar: "/placeholder.svg?height=40&width=40",
      bio: "Chef, food blogger, and culinary instructor. Passionate about sustainable cooking and local ingredients.",
      location: "Chicago, IL",
      socialLinks: [
        { platform: "Instagram", url: "#", username: "@emilycooks" },
        { platform: "Facebook", url: "#", username: "EmilyDavisCooking" },
        { platform: "YouTube", url: "#", username: "EmilysCookingChannel" },
      ],
      lastContacted: "2023-04-25",
      firstContacted: "2020-08-12",
      emailCount: 64,
    },
    recipients: [
      {
        name: "You",
        email: "your.email@gmail.com",
      },
    ],
    content: `Hi there!

Would you like to grab dinner this weekend? There's a new Italian restaurant downtown that I've been wanting to try.

They have great reviews, and I heard their pasta is amazing. Let me know if you're free either Saturday or Sunday evening.

Hope you can make it!

Emily`,
    date: "2023-04-30T18:05:00",
    read: true,
    flagged: false,
    snoozed: false,
    archived: false,
    deleted: false,
    account: "personal",
  },
  {
    id: "6",
    subject: "Quarterly Report - Q1 2023",
    sender: {
      name: "Finance Team",
      email: "finance@company.com",
      avatar: "/placeholder.svg?height=40&width=40",
      organization: {
        name: "Acme Corp",
        logo: "/placeholder.svg?height=20&width=20&text=AC",
        website: "https://acmecorp.example.com",
      },
      role: "Finance Department",
      lastContacted: "2023-01-28",
      firstContacted: "2021-04-28",
      emailCount: 24,
    },
    recipients: [
      {
        name: "All Staff",
        email: "all-staff@company.com",
      },
    ],
    content: `Dear Team,

Attached is the quarterly financial report for Q1 2023. Key highlights:

- Revenue increased by 15% compared to Q4 2022
- New client acquisition up by 22%
- Operating costs reduced by 8%

Please review the full report for detailed analysis and projections for Q2.

Thank you,
Finance Team`,
    date: "2023-04-28T11:30:00",
    read: true,
    flagged: false,
    snoozed: false,
    archived: false,
    deleted: false,
    attachments: [
      {
        name: "Q1_2023_Report.xlsx",
        size: "2.3 MB",
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        url: "#",
      },
      {
        name: "Q1_2023_Presentation.pptx",
        size: "4.7 MB",
        type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        url: "#",
      },
    ],
    account: "work",
  },
  {
    id: "7",
    subject: "Your flight confirmation",
    sender: {
      name: "Airline Bookings",
      email: "bookings@airline.com",
      avatar: "/placeholder.svg?height=40&width=40",
      organization: {
        name: "Sky Airlines",
        logo: "/placeholder.svg?height=20&width=20&text=SA",
        website: "https://skyairlines.example.com",
      },
      role: "Booking System",
      lastContacted: "2023-02-15",
      firstContacted: "2022-09-10",
      emailCount: 8,
    },
    recipients: [
      {
        name: "You",
        email: "your.email@gmail.com",
      },
    ],
    content: `Dear Passenger,

Your flight has been confirmed. Here are your flight details:

Flight: AA1234
Date: June 15, 2023
Departure: New York (JFK) at 10:30 AM
Arrival: San Francisco (SFO) at 1:45 PM

Please arrive at the airport at least 2 hours before your scheduled departure. Your boarding pass is attached to this email.

Safe travels!
Airline Bookings`,
    date: "2023-04-25T09:45:00",
    read: true,
    flagged: true,
    snoozed: false,
    archived: false,
    deleted: false,
    attachments: [
      {
        name: "Boarding_Pass.pdf",
        size: "312 KB",
        type: "application/pdf",
        url: "#",
      },
    ],
    account: "personal",
  },
  {
    id: "8",
    subject: "Website Redesign Proposal",
    sender: {
      name: "Design Agency",
      email: "contact@designagency.com",
      avatar: "/placeholder.svg?height=40&width=40",
      organization: {
        name: "Creative Design",
        logo: "/placeholder.svg?height=20&width=20&text=CD",
        website: "https://creativedesign.example.com",
      },
      bio: "Award-winning design agency specializing in brand identity, web design, and user experience.",
      location: "Austin, TX",
      socialLinks: [
        { platform: "Dribbble", url: "#", username: "creativedesign" },
        { platform: "Behance", url: "#", username: "creative-design-agency" },
        { platform: "Instagram", url: "#", username: "@creativedesignco" },
      ],
      lastContacted: "2023-04-15",
      firstContacted: "2023-03-01",
      emailCount: 12,
    },
    recipients: [
      {
        name: "You",
        email: "your.name@company.com",
      },
    ],
    content: `Hello,

Thank you for the opportunity to work on your website redesign project. We've prepared a comprehensive proposal based on our discussions.

The proposal includes:
- Project scope and timeline
- Design concepts
- Technical specifications
- Cost breakdown

Please review the attached document and let us know if you have any questions or would like to schedule a call to discuss further.

Best regards,
Design Agency Team`,
    date: "2023-04-22T16:10:00",
    read: false,
    flagged: false,
    snoozed: false,
    archived: false,
    deleted: false,
    attachments: [
      {
        name: "Website_Redesign_Proposal.pdf",
        size: "5.8 MB",
        type: "application/pdf",
        url: "#",
      },
    ],
    account: "work",
  },
]
