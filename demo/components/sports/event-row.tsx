"use client"

import Link from "next/link"
import { useBetSlip } from "@/lib/client/stores"
import { OddsButton, Badge } from "@/components/ui/kit"
import { Clock } from "lucide-react"

export interface EventDto {
  id: string
  home: string
  away: string
  startsAt: string
  status: string
  homeScore: number
  awayScore: number
  clockSeconds: number
  sport: { name: string; slug: string } | null
  competition: { name: string } | null
  marketCount: number
  primaryMarket: { id: string; name: string; status: string } | null
  primarySelections: { id: string; name: string; odds: number }[]
}

function fmtClock(sec: number) {
  const m = Math.floor(sec / 60)
  return `${m}'`
}

export function EventRow({ ev }: { ev: EventDto }) {
  const { toggle, has } = useBetSlip()
  const live = ev.status === "LIVE"
  const start = new Date(ev.startsAt)
  const eventLabel = `${ev.home} v ${ev.away}`

  return (
    <div className="flex items-stretch gap-3 border-b border-border/60 px-3 py-2 last:border-0 hover:bg-accent/40">
      <div className="flex min-w-0 flex-1 flex-col justify-center gap-1">
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
          {live ? (
            <Badge variant="live">
              <span className="mr-0.5 inline-block size-1.5 animate-pulse rounded-full bg-current" />
              Live {fmtClock(ev.clockSeconds)}
            </Badge>
          ) : (
            <span className="inline-flex items-center gap-1">
              <Clock className="size-3" />
              {start.toLocaleDateString("en", { day: "2-digit", month: "2-digit" })}{" "}
              {start.toLocaleTimeString("en", { hour: "2-digit", minute: "2-digit" })}
            </span>
          )}
          <span className="truncate">{ev.competition?.name}</span>
        </div>
        <Link href={`/event/${ev.id}`} className="min-w-0">
          <div className="flex items-center justify-between gap-2">
            <span className="truncate text-sm font-medium">{ev.home}</span>
            {live && <span className="font-mono text-sm font-bold tabular-nums text-[var(--live)]">{ev.homeScore}</span>}
          </div>
          <div className="flex items-center justify-between gap-2">
            <span className="truncate text-sm font-medium">{ev.away}</span>
            {live && <span className="font-mono text-sm font-bold tabular-nums text-[var(--live)]">{ev.awayScore}</span>}
          </div>
        </Link>
      </div>

      <div className="flex w-[220px] shrink-0 items-center gap-1.5 sm:w-[260px]">
        {ev.primarySelections.length > 0 ? (
          ev.primarySelections.slice(0, 3).map((sel) => (
            <OddsButton
              key={sel.id}
              label={sel.name}
              odds={sel.odds}
              active={has(sel.id)}
              disabled={ev.primaryMarket?.status !== "OPEN"}
              onClick={() =>
                toggle({
                  selectionId: sel.id,
                  eventId: ev.id,
                  eventLabel,
                  marketName: ev.primaryMarket?.name ?? "1X2",
                  selectionName: sel.name,
                  odds: sel.odds,
                })
              }
            />
          ))
        ) : (
          <span className="text-xs text-muted-foreground">No market</span>
        )}
      </div>
      <Link
        href={`/event/${ev.id}`}
        className="hidden shrink-0 items-center text-[11px] font-medium text-muted-foreground hover:text-primary sm:flex"
      >
        +{ev.marketCount}
      </Link>
    </div>
  )
}
