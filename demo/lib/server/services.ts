import { eventLabel, getDb, nextId, pushTx, type Db } from "./store"
import type { Bet, BetSelectionRef, User, Wallet } from "@/lib/domain/types"

export function walletFor(userId: string): Wallet {
  const db = getDb()
  let w = db.wallets.find((x) => x.userId === userId)
  if (!w) {
    w = { userId, available: 0, bonus: 0 }
    db.wallets.push(w)
  }
  return w
}

function round2(n: number) {
  return Math.round(n * 100) / 100
}

export interface PlaceBetInput {
  selectionIds: string[]
  stake: number
}

export function placeBet(user: User, input: PlaceBetInput): { bet: Bet } | { error: string } {
  const db = getDb()
  const stake = Number(input.stake)
  if (!Array.isArray(input.selectionIds) || input.selectionIds.length === 0) return { error: "No selections" }
  if (!Number.isFinite(stake) || stake <= 0) return { error: "Stake must be a positive number" }
  if (stake > 5000) return { error: "Stake exceeds demo limit of 5000 credits" }

  const refs: BetSelectionRef[] = []
  let combined = 1
  const seenEvents = new Set<string>()
  for (const sid of input.selectionIds) {
    const sel = db.selections.find((s) => s.id === sid)
    if (!sel) return { error: "Selection not found" }
    const market = db.markets.find((m) => m.id === sel.marketId)!
    if (market.status !== "OPEN") return { error: `Market "${market.name}" is suspended` }
    const ev = db.events.find((e) => e.id === market.eventId)!
    if (ev.status === "FINISHED" || ev.status === "SUSPENDED") return { error: "Event unavailable" }
    if (seenEvents.has(ev.id)) return { error: "Cannot combine multiple selections from the same event" }
    seenEvents.add(ev.id)
    combined *= sel.odds
    refs.push({
      selectionId: sel.id,
      eventId: ev.id,
      marketName: market.name,
      selectionName: sel.name,
      eventLabel: eventLabel(db, ev),
      oddsAtPlacement: sel.odds,
    })
  }

  const wallet = walletFor(user.id)
  if (wallet.available < stake) return { error: "Insufficient DEMO CREDITS" }

  combined = round2(combined)
  const bet: Bet = {
    id: nextId("bet"),
    ticketCode: "NX" + Math.floor(100000 + Math.random() * 899999),
    userId: user.id,
    betType: refs.length > 1 ? "MULTI" : "SINGLE",
    status: "SUBMITTED",
    stake: round2(stake),
    combinedOdds: combined,
    potentialPayout: round2(stake * combined),
    selections: refs,
    createdAt: new Date().toISOString(),
    settledAt: null,
  }
  db.bets.unshift(bet)
  wallet.available = round2(wallet.available - stake)
  pushTx(db, user.id, "MOCK_BET", stake, bet.ticketCode, "Mock bet placed")
  return { bet }
}

// operator settles a bet (WON/LOST/VOID). Handles wallet effects for demo credits.
export function settleBet(actor: User, betId: string, outcome: "WON" | "LOST" | "VOID"): { bet: Bet } | { error: string } {
  const db = getDb()
  const bet = db.bets.find((b) => b.id === betId)
  if (!bet) return { error: "Bet not found" }
  if (bet.status !== "SUBMITTED" && bet.status !== "OPEN") return { error: `Cannot settle a bet in status ${bet.status}` }
  const wallet = walletFor(bet.userId)
  if (outcome === "WON") {
    wallet.available = round2(wallet.available + bet.potentialPayout)
    pushTx(db, bet.userId, "MOCK_PAYOUT", bet.potentialPayout, bet.ticketCode, "Mock winning payout")
  } else if (outcome === "VOID") {
    wallet.available = round2(wallet.available + bet.stake)
    pushTx(db, bet.userId, "MOCK_REFUND", bet.stake, bet.ticketCode, "Mock void refund")
  }
  bet.status = outcome
  bet.settledAt = new Date().toISOString()
  return { bet }
}

export function ledgerAdjust(actor: User, userId: string, amount: number, note: string): { ok: true } | { error: string } {
  const db = getDb()
  if (!Number.isFinite(amount) || amount === 0) return { error: "Amount must be a non-zero number" }
  const wallet = walletFor(userId)
  if (wallet.available + amount < 0) return { error: "Adjustment would make balance negative" }
  wallet.available = round2(wallet.available + amount)
  pushTx(db, userId, "MOCK_ADJUSTMENT", amount, "ADJ" + Date.now(), note || "Manual demo adjustment")
  return { ok: true }
}

export function safeUser(u: User) {
  const { password, ...rest } = u
  return rest
}

export function publicWallet(db: Db, userId: string) {
  const w = walletFor(userId)
  return { available: w.available, bonus: w.bonus, currency: "DEMO" }
}
