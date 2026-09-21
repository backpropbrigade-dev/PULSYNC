import type { RoleName } from "./permissions"

export type AccountStatus = "ACTIVE" | "SUSPENDED" | "LOCKED"
export type BetStatus = "OPEN" | "SUBMITTED" | "WON" | "LOST" | "VOID" | "CANCELLED"
export type EventStatus = "SCHEDULED" | "LIVE" | "FINISHED" | "SUSPENDED"
export type MarketStatus = "OPEN" | "SUSPENDED" | "SETTLED"
export type PromotionStatus = "DRAFT" | "REVIEW" | "PUBLISHED" | "EXPIRED" | "ARCHIVED"
export type TicketStatus = "OPEN" | "ASSIGNED" | "IN_PROGRESS" | "WAITING" | "RESOLVED" | "CLOSED"
export type RiskStatus = "OPEN" | "UNDER_REVIEW" | "ACTION_REQUIRED" | "RESOLVED"
export type CmsStatus = "DRAFT" | "REVIEW" | "PUBLISHED"
export type TxType = "MOCK_BET" | "MOCK_PAYOUT" | "MOCK_ADJUSTMENT" | "MOCK_REFUND" | "MOCK_BONUS"
export type LedgerAccount = "CUSTOMER_WALLET" | "PENDING_BETS" | "HOUSE" | "BONUS"

export interface User {
  id: string
  email: string
  password: string
  displayName: string
  roles: RoleName[]
  status: AccountStatus
  city: string
  isDemoSeed: boolean
  createdAt: string
}

export interface Wallet {
  userId: string
  available: number
  bonus: number
}

export interface Transaction {
  id: string
  userId: string
  type: TxType
  amount: number
  reference: string
  note: string
  createdAt: string
}

export interface LedgerEntry {
  id: string
  transactionId: string
  userId: string
  account: LedgerAccount
  debit: number
  credit: number
  createdAt: string
}

export interface Sport {
  id: string
  slug: string
  name: string
  sortOrder: number
}

export interface Competition {
  id: string
  sportId: string
  name: string
  country: string
}

export interface Participant {
  id: string
  sportId: string
  name: string
}

export interface Event {
  id: string
  competitionId: string
  homeId: string
  awayId: string
  startsAt: string
  status: EventStatus
  homeScore: number
  awayScore: number
  clockSeconds: number
  simSeed: number
}

export interface Selection {
  id: string
  marketId: string
  name: string
  odds: number
}

export interface Market {
  id: string
  eventId: string
  name: string
  status: MarketStatus
}

export interface BetSelectionRef {
  selectionId: string
  eventId: string
  marketName: string
  selectionName: string
  eventLabel: string
  oddsAtPlacement: number
}

export interface Bet {
  id: string
  ticketCode: string
  userId: string
  betType: "SINGLE" | "MULTI"
  status: BetStatus
  stake: number
  combinedOdds: number
  potentialPayout: number
  selections: BetSelectionRef[]
  createdAt: string
  settledAt: string | null
}

export interface CasinoGame {
  id: string
  providerId: string
  name: string
  category: string
  mockRtp: number
  isNew: boolean
  isPopular: boolean
  isFeatured: boolean
}

export interface Promotion {
  id: string
  title: string
  body: string
  theme: string
  status: PromotionStatus
  publishedAt: string | null
  createdAt: string
}

export interface Banner {
  id: string
  title: string
  subtitle: string
  theme: string
  sortOrder: number
}

export interface CMSContent {
  id: string
  contentType: string
  title: string
  body: string
  status: CmsStatus
  publishedAt: string | null
}

export interface SupportMessage {
  id: string
  ticketId: string
  authorId: string
  authorName: string
  body: string
  internal: boolean
  createdAt: string
}

export interface SupportTicket {
  id: string
  customerId: string
  customerName: string
  assigneeId: string | null
  subject: string
  category: string
  status: TicketStatus
  createdAt: string
  updatedAt: string
}

export interface RiskAlert {
  id: string
  userId: string
  userName: string
  alertType: string
  severity: "LOW" | "MEDIUM" | "HIGH"
  status: RiskStatus
  details: string
  createdAt: string
}

export interface Notification {
  id: string
  userId: string
  title: string
  body: string
  read: boolean
  createdAt: string
}

export interface AuditLog {
  id: string
  actorId: string
  actorRole: string
  action: string
  resourceType: string
  resourceId: string
  reason: string
  createdAt: string
}

export interface FeatureFlag {
  key: string
  enabled: boolean
  description: string
}

export interface SystemSetting {
  key: string
  value: string
}
