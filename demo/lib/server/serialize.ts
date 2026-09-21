import { getDb, type Db } from "./store"
import type { Event } from "@/lib/domain/types"

export function participantName(db: Db, id: string) {
  return db.participants.find((p) => p.id === id)?.name ?? "Unknown"
}

export function serializeEvent(db: Db, ev: Event) {
  const comp = db.competitions.find((c) => c.id === ev.competitionId)
  const sport = comp ? db.sports.find((s) => s.id === comp.sportId) : undefined
  const markets = db.markets.filter((m) => m.eventId === ev.id)
  const primary = markets.find((m) => m.name === "1X2") ?? markets[0]
  const primarySelections = primary
    ? db.selections
        .filter((s) => s.marketId === primary.id)
        .map((s) => ({ id: s.id, name: s.name, odds: s.odds }))
    : []
  return {
    id: ev.id,
    home: participantName(db, ev.homeId),
    away: participantName(db, ev.awayId),
    startsAt: ev.startsAt,
    status: ev.status,
    homeScore: ev.homeScore,
    awayScore: ev.awayScore,
    clockSeconds: ev.clockSeconds,
    sport: sport ? { id: sport.id, slug: sport.slug, name: sport.name } : null,
    competition: comp ? { id: comp.id, name: comp.name, country: comp.country } : null,
    marketCount: markets.length,
    primaryMarket: primary ? { id: primary.id, name: primary.name, status: primary.status } : null,
    primarySelections,
  }
}

export function serializeEventDetail(db: Db, ev: Event) {
  const base = serializeEvent(db, ev)
  const markets = db.markets
    .filter((m) => m.eventId === ev.id)
    .map((m) => ({
      id: m.id,
      name: m.name,
      status: m.status,
      selections: db.selections
        .filter((s) => s.marketId === m.id)
        .map((s) => ({ id: s.id, name: s.name, odds: s.odds })),
    }))
  return { ...base, markets }
}
