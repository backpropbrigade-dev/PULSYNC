import axios from 'axios'

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined)?.trim() || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface SportItem {
  id: string
  slug: string
  name: string
  eventCount: number
  liveCount: number
}

export interface SelectionItem {
  id: string
  name: string
  odds: number
}

export interface EventItem {
  id: string
  match_id: string
  home: string
  away: string
  startsAt: string
  status: string
  homeScore?: number
  awayScore?: number
  clockSeconds?: number
  sport: { name: string; slug: string }
  competition: { name: string }
  marketCount: number
  primaryMarket: { id: string; name: string; status: string }
  primarySelections: SelectionItem[]
}

export interface DatasetSummary {
  dataset_name: string
  total_records: number
  date_range: { from: string; to: string }
  unique_players: number
  unique_sports: number
  unique_events: number
  data_quality: {
    duplicate_rows: number
    missing_player_id: number
    data_quality_score: number
  }
}

export interface PlayerProfileData {
  user_id: string
  profile_source: string
  preferred_sport: string
  activity_level: string
  historical_activity: {
    total_actions: number
    unique_sports_explored: number
    sports_breakdown: Record<string, number>
  }
  sports_interest: Record<string, number>
}

export interface RecommendationItem {
  id: string
  title: string
  description: string
  score: number
  reason: string
  action_label: string
  content_id?: string
  content_type?: string
}

export interface SessionIntel {
  session_id?: string
  user_id?: string
  intent: string
  intent_confidence: number
  intent_reason?: string
  // Machine 3 signals
  transaction_intent: 'LOW' | 'MEDIUM' | 'HIGH'
  information_interest: 'LOW' | 'MEDIUM' | 'HIGH'
  engagement_state: 'NORMAL' | 'VALUE_SEEKING' | 'RESPECT_EXIT' | 'LOW_PRESSURE'
  recommendation_mode: 'NORMAL' | 'VALUE_SEEKING' | 'RESPECT_EXIT' | 'LOW_PRESSURE'
  engagement_message?: string
  explicit_exit?: boolean
  friction_level: string
  friction_score?: number
  abandonment_probability: number
  session_quality?: number
  session_quality_score?: number
  continuation_probability?: number
  model_source?: string
  model_versions?: {
    intent?: string
    abandonment?: string
    continuation?: string
  }
  recommendations?: RecommendationItem[]
  top_recommendation?: RecommendationItem | null
  compliance?: {
    betting_eligible: boolean
    self_excluded: boolean
    age_verified: boolean
    kyc_verified: boolean
    login_required: boolean
  }
}

export async function fetchSports(): Promise<SportItem[]> {
  try {
    const res = await api.get<{ sports: SportItem[] }>('/api/sports')
    return res.data.sports || []
  } catch (e) {
    console.error('Failed to fetch sports from API', e)
    return []
  }
}

export async function fetchEvents(sport = 'all', day = 'all', status = ''): Promise<EventItem[]> {
  try {
    const params: Record<string, string> = { sport, day }
    if (status) params.status = status
    const res = await api.get<{ events: EventItem[] }>('/api/events', { params })
    return res.data.events || []
  } catch (e) {
    console.error('Failed to fetch events from API', e)
    return []
  }
}

export async function fetchDatasetSummary(): Promise<DatasetSummary | null> {
  try {
    const res = await api.get<DatasetSummary>('/api/dashboard/dataset-summary')
    return res.data
  } catch (e) {
    console.error('Failed to fetch dataset summary', e)
    return null
  }
}

export async function fetchUserProfile(userId = 'usr_demo'): Promise<PlayerProfileData | null> {
  try {
    const res = await api.get<PlayerProfileData>(`/api/users/${userId}/profile`)
    return res.data
  } catch (e) {
    console.error('Failed to fetch user profile', e)
    return null
  }
}

export async function fetchAnalytics(): Promise<any> {
  try {
    const res = await api.get('/api/analytics')
    return res.data
  } catch (e) {
    console.error('Failed to fetch analytics', e)
    return null
  }
}

export async function createSession(anonymousId: string): Promise<string> {
  const res = await api.post('/api/sessions', { anonymous_user_id: anonymousId })
  const sessionId = res.data.session_id || res.data.id
  if (!sessionId) {
    throw new Error('Session API returned no session identifier')
  }
  localStorage.setItem('pulsync_session_id', sessionId)
  return sessionId
}

export function getActiveSessionId(): string | null {
  return localStorage.getItem('pulsync_session_id')
}

export async function trackSessionEvent(sessionId: string, eventType: string, page: string, action: string) {
  const res = await api.post(`/api/sessions/${sessionId}/events`, {
    event_type: eventType,
    page,
    action,
    timestamp: new Date().toISOString()
  })
  window.dispatchEvent(new CustomEvent('pulsync-session-updated', { detail: sessionId }))
  return res.data
}

export async function fetchRecommendations(sessionId: string): Promise<RecommendationItem[]> {
  try {
    const res = await api.get<{ recommendations: RecommendationItem[] }>(`/api/recommendations/${sessionId}`)
    return res.data.recommendations || []
  } catch (e) {
    return []
  }
}

export async function fetchSessionIntelligence(sessionId: string): Promise<SessionIntel | null> {
  try {
    const res = await api.get<SessionIntel>(`/api/sessions/${sessionId}/intelligence`)
    return res.data
  } catch (e) {
    return null
  }
}

export async function loginApi(sessionId?: string) {
  const res = await api.post('/api/auth/login', { session_id: sessionId })
  return res.data
}

export interface BettingEligibilityResult {
  user_id?: string
  eligible: boolean
  age_verified: boolean
  kyc_verified: boolean
  self_excluded: boolean
  reason: string
  status: string
  demo: boolean
}

export async function verifyAgeApi(userId: string, age: number, birthDate?: string) {
  try {
    const res = await api.post('/api/compliance/age-verification', {
      user_id: userId,
      anonymous_user_id: userId,
      age,
      birth_date: birthDate
    })
    return res.data
  } catch (e) {
    return { verified: false, status: 'AGE_RESTRICTED' }
  }
}

export async function submitKycDemoApi(userId: string, documentType = 'National ID') {
  try {
    const res = await api.post('/api/compliance/kyc-demo', {
      user_id: userId,
      anonymous_user_id: userId,
      document_type: documentType
    })
    return res.data
  } catch (e) {
    return { kyc_verified: false, status: 'KYC_FAILED' }
  }
}

export async function checkSelfExclusionApi(userId: string) {
  try {
    const res = await api.post('/api/compliance/self-exclusion-check', {
      user_id: userId,
      anonymous_user_id: userId
    })
    return res.data
  } catch (e) {
    return { excluded: false, eligible: true }
  }
}

export async function checkBettingEligibilityApi(userId: string, sessionId?: string): Promise<BettingEligibilityResult> {
  const res = await api.post<BettingEligibilityResult>('/api/compliance/betting-eligibility', {
    user_id: userId,
    anonymous_user_id: userId,
    session_id: sessionId
  })
  return res.data
}

export async function placeBetApi(userId: string, selections: any[], stake: number, sessionId?: string) {
  try {
    const res = await api.post('/api/bets', {
      user_id: userId,
      anonymous_user_id: userId,
      session_id: sessionId,
      selections,
      stake
    })
    return res.data
  } catch (e: any) {
    if (e.response?.data?.detail) {
      throw e.response.data.detail
    }
    throw e
  }
}

// ==================================================
// PULSYNC Session & ROI Intelligence APIs (Machine 4)
// ==================================================
export interface ImpactKPI {
  value: any
  label: string
  type: string
  period?: string
  share_pct?: number
  badge?: string
}

export interface ImpactSummary {
  dataset: {
    name: string
    records: number
    players: number
    sessions: number
    date_start: string
    date_end: string
    unique_sports: number
    inactivity_threshold_min: number
    session_type: string
    data_quality_score: number
  }
  kpi_cards: Record<string, ImpactKPI>
  evidence: {
    type: string
    causal_claim: boolean
    disclaimer: string
  }
}

export interface FunnelStage {
  stage: string
  count: number
  rate_pct: number
}

export interface DailyTrend {
  date: string
  sessions: number
  active_players: number
  value_seeking_sessions: number
  respect_exit_sessions: number
  abandonment_rate: number
  return_7d_rate: number
}

export interface SessionHealthData {
  total_sessions: number
  active_players: number
  average_duration_sec: number
  actions_per_session: number
  information_interactions_per_session: number
  session_completion_rate: number
  abandonment_rate: number
  friction_score_avg: number
  session_quality_avg: number
  funnel: FunnelStage[]
  daily_trends: DailyTrend[]
}

export interface MatrixCell {
  transaction_intent: string
  information_interest: string
  sessions: number
  players: number
  session_share: number
  player_share: number
  return_7d_rate: number
  is_pulsync_opportunity: boolean
}

export interface SegmentInfo {
  name: string
  sessions: number
  players: number
  session_share: number
  player_share: number
  return_1d_rate: number
  return_3d_rate: number
  return_7d_rate: number
  subsequent_session_rate: number
  subsequent_stake_rate: number
  historical_stake_exposure: number
  average_original_stake_eur: number
  average_subsequent_stake_eur: number
}

export interface ReplayCohort {
  name?: string
  sessions: number
  players: number
  return_1d_rate: number
  return_3d_rate: number
  return_7d_rate: number
  subsequent_session_rate: number
  subsequent_stake_rate: number
  avg_time_to_return_days: number
}

export interface ReplayData {
  value_seeking: ReplayCohort
  comparison_cohort: ReplayCohort
  observed_difference_pp: number
  relative_difference_pct: number
  confidence_interval_95: [number, number]
  z_statistic: number
  p_value: string
  statistically_significant: boolean
  average_subsequent_stake_eur: number
  evidence_type: string
}

export interface OpportunityData {
  target_segment: string
  definition: string
  sessions: number
  session_share_pct: number
  players: number
  player_share_pct: number
  historical_stake_exposure_eur: number
  return_7d_rate_pct: number
  observed_gap_pp: number
  relative_difference_pct: number
  evidence_type: string
}

export interface ROISensitivityItem {
  realization_pct: number
  annual_value_eur: number
  annual_net_value_eur: number
  roi_percent: number
  is_positive: boolean
}

export interface ROIWaterfallItem {
  step: string
  amount: number
  unit: string
}

export interface ROISimulationResult {
  scenario: string
  inputs: {
    scenario_realization_pct: number
    inference_cost_per_call: number
    api_cost_per_call: number
    hosting_cost_monthly: number
    storage_cost_monthly: number
    engineering_cost: number
    monthly_sessions: number
    average_subsequent_stake: number
  }
  outputs: {
    monthly_target_sessions: number
    incremental_returning_sessions: number
    monthly_scenario_value_eur: number
    annual_scenario_value_eur: number
    monthly_operating_cost_eur: number
    annual_operating_cost_eur: number
    monthly_net_value_eur: number
    annual_net_value_eur: number
    roi_percent: number
    payback_months: number | null
    payback_status: string
  }
  sensitivity: ROISensitivityItem[]
  waterfall: ROIWaterfallItem[]
}

export interface ImpactCaseSection {
  number: number
  title: string
  content: string
}

export interface ImpactCaseData {
  title: string
  tagline: string
  sections: ImpactCaseSection[]
  metrics: ROISimulationResult
}

export interface MethodologyData {
  session_definition: string
  session_type: string
  information_interest_proxy: string
  target_segment_definition: string
  comparison_cohort: string
  return_windows: string[]
  statistical_test: string
  causal_claim: boolean
  causal_disclaimer: string
}

export interface MetricsChainLevel {
  level: number
  name: string
  metrics: Array<{
    name: string
    target: string
    current: string
    status: string
  }>
}

export interface MetricsChainData {
  levels: MetricsChainLevel[]
  signals: {
    positive: string[]
    negative_monitored: string[]
    compliance_guardrails: Array<{
      rule: string
      violations: number
      status: string
    }>
  }
}

export async function fetchImpactSummary(): Promise<ImpactSummary> {
  const res = await api.get<ImpactSummary>('/api/impact/summary')
  return res.data
}

export async function fetchImpactSessionHealth(): Promise<SessionHealthData> {
  const res = await api.get<SessionHealthData>('/api/impact/session-health')
  return res.data
}

export async function fetchImpactMatrix(): Promise<MatrixCell[]> {
  const res = await api.get<MatrixCell[]>('/api/impact/matrix')
  return res.data
}

export async function fetchImpactSegments(): Promise<Record<string, SegmentInfo>> {
  const res = await api.get<Record<string, SegmentInfo>>('/api/impact/segments')
  return res.data
}

export async function fetchImpactReplay(): Promise<ReplayData> {
  const res = await api.get<ReplayData>('/api/impact/replay')
  return res.data
}

export async function fetchImpactOpportunity(): Promise<OpportunityData> {
  const res = await api.get<OpportunityData>('/api/impact/opportunity')
  return res.data
}

export async function simulateROI(assumptions: any): Promise<ROISimulationResult> {
  const res = await api.post<ROISimulationResult>('/api/impact/roi/simulate', assumptions)
  return res.data
}

export async function fetchImpactCase(scenario: string = 'base'): Promise<ImpactCaseData> {
  const res = await api.get<ImpactCaseData>(`/api/impact/impact-case?scenario=${scenario}`)
  return res.data
}

export async function fetchImpactMethodology(): Promise<MethodologyData> {
  const res = await api.get<MethodologyData>('/api/impact/methodology')
  return res.data
}

export async function fetchImpactMetricsChain(): Promise<MetricsChainData> {
  const res = await api.get<MetricsChainData>('/api/impact/metrics-chain')
  return res.data
}
