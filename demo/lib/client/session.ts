import { apiGet, apiPost, isExternalApiConfigured } from "@/lib/client/api"

export interface SessionIntelligence {
  intent?: { label?: string; confidence?: number; reason?: string }
  abandonment?: { probability?: number; risk?: string; reason?: string }
  friction?: { score?: number; level?: string; reason?: string }
  recommendations?: unknown[]
  guidance?: { show?: boolean; type?: string; message?: string; content_id?: string }
  session_quality?: { score?: number; label?: string }
}

export interface SessionState {
  session_id: string
  user_id?: string
  started_at?: string
  intelligence?: SessionIntelligence
}

const SESSION_KEY = "pulsync.session"
const USER_KEY = "pulsync.anonymous_user_id"

function readStoredSession(): SessionState | null {
  if (typeof window === "undefined") return null
  const raw = window.sessionStorage.getItem(SESSION_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as SessionState
  } catch {
    window.sessionStorage.removeItem(SESSION_KEY)
    return null
  }
}

function anonymousUserId(): string {
  if (typeof window === "undefined") return ""
  const existing = window.localStorage.getItem(USER_KEY)
  if (existing) return existing
  const id = crypto.randomUUID()
  window.localStorage.setItem(USER_KEY, id)
  return id
}

let inFlightSessionPromise: Promise<SessionState | null> | null = null

export async function recoverOrCreateSession(): Promise<SessionState | null> {
  if (!isExternalApiConfigured()) return null
  const stored = readStoredSession()
  if (stored?.session_id) return stored

  if (inFlightSessionPromise) return inFlightSessionPromise

  inFlightSessionPromise = (async () => {
    try {
      const created = await apiPost<SessionState>("/api/sessions", {
        anonymous_user_id: anonymousUserId(),
      })
      if (!created.session_id) throw new Error("Session service returned no session_id")
      window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(created))
      return created
    } finally {
      inFlightSessionPromise = null
    }
  })()

  return inFlightSessionPromise
}

export async function verifyAccess(age: number): Promise<{ verified: boolean; minimum_age?: number }> {
  const ageResult = await apiPost<{ verified: boolean; minimum_age?: number }>(
    "/api/compliance/age-verification",
    { age },
  )
  if (!ageResult.verified) throw new Error("Age verification was not accepted")

  const exclusionResult = await apiPost<{ eligible: boolean }>(
    "/api/compliance/self-exclusion-check",
    { anonymous_user_id: anonymousUserId() },
  )
  if (!exclusionResult.eligible) throw new Error("Access is unavailable due to self-exclusion")
  return ageResult
}

export async function trackEvent(
  event: Omit<Record<string, unknown>, "session_id" | "timestamp">,
): Promise<SessionIntelligence | null> {
  const session = readStoredSession()
  if (!session?.session_id || !isExternalApiConfigured()) return null
  const response = await apiPost<{ intelligence?: SessionIntelligence }>(
    `/api/sessions/${encodeURIComponent(session.session_id)}/events`,
    { ...event, session_id: session.session_id, timestamp: new Date().toISOString() },
  )
  const intelligence = response.intelligence
  if (intelligence) {
    const updated = { ...session, intelligence }
    window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(updated))
  }
  return intelligence || null
}

export async function getRecommendations(sessionId: string): Promise<unknown> {
  return apiGet(`/api/recommendations/${encodeURIComponent(sessionId)}`)
}

export async function submitRecommendationFeedback(
  sessionId: string,
  recommendationId: string,
  action: "clicked" | "dismissed" | "ignored",
): Promise<unknown> {
  return apiPost(`/api/recommendations/${encodeURIComponent(sessionId)}/feedback`, {
    recommendation_id: recommendationId,
    action,
  })
}

export async function submitOutcome(
  outcome: Record<string, unknown> & { decision: string },
): Promise<unknown> {
  return apiPost("/api/outcomes", outcome)
}
