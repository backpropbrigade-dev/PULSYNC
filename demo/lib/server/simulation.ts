import { getDb } from "./store"

// Advance live events + drift odds based on real elapsed time. Deterministic-ish per event seed.
export function tickSimulation() {
  const db = getDb()
  const now = Date.now()
  const elapsed = (now - db.lastTick) / 1000
  if (elapsed < 1) return
  db.lastTick = now

  for (const ev of db.events) {
    if (ev.status !== "LIVE") continue
    ev.clockSeconds += Math.min(elapsed * 6, 120) // accelerated mock clock
    // occasional score change
    const seedRnd = ((ev.simSeed * (Math.floor(now / 15000) + 1)) % 100) / 100
    if (seedRnd > 0.97) {
      if (seedRnd > 0.985) ev.homeScore += 1
      else ev.awayScore += 1
    }
    if (ev.clockSeconds > 5400) {
      ev.status = "FINISHED"
      ev.clockSeconds = 5400
    }
  }

  // drift odds on live events' markets
  const liveEventIds = new Set(db.events.filter((e) => e.status === "LIVE").map((e) => e.id))
  const liveMarketIds = new Set(db.markets.filter((m) => liveEventIds.has(m.eventId) && m.status === "OPEN").map((m) => m.id))
  for (const sel of db.selections) {
    if (!liveMarketIds.has(sel.marketId)) continue
    const drift = (Math.sin(now / 4000 + sel.odds * 10) * 0.04)
    sel.odds = Math.max(1.05, Math.round((sel.odds + drift) * 100) / 100)
  }
}
