"use client"

import useSWR from "swr"
import { useBetSlip } from "@/lib/client/stores"
import { Card, Skeleton, OddsButton, Badge, EmptyState } from "@/components/ui/kit"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

interface MarketDto {
  id: string
  name: string
  status: string
  selections: { id: string; name: string; odds: number }[]
}
interface EventDetailDto {
  id: string
  home: string
  away: string
  startsAt: string
  status: string
  homeScore: number
  awayScore: number
  clockSeconds: number
  competition: { name: string } | null
  sport: { name: string } | null
  markets: MarketDto[]
}

export function EventDetail({ id }: { id: string }) {
  const { data, isLoading, error } = useSWR<{ event: EventDetailDto }>(`/api/events/${id}`, { refreshInterval: 4000 })
  const { toggle, has } = useBetSlip()

  if (isLoading)
    return (
      <div className="flex flex-col gap-3">
        <Skeleton className="h-24" />
        <Skeleton className="h-40" />
        <Skeleton className="h-40" />
      </div>
    )
  if (error || !data?.event) return <EmptyState title="Event not found" hint="It may have been removed from the mock feed." />

  const ev = data.event
  const live = ev.status === "LIVE"
  const eventLabel = `${ev.home} v ${ev.away}`

  return (
    <div className="flex flex-col gap-3">
      <Link href="/sport" className="inline-flex w-fit items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="size-4" /> Back
      </Link>
      <Card className="p-4">
        <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
          <span>{ev.sport?.name}</span>
          <span>·</span>
          <span>{ev.competition?.name}</span>
          {live && <Badge variant="live">Live {Math.floor(ev.clockSeconds / 60)}&apos;</Badge>}
          <Badge variant={ev.status === "FINISHED" ? "muted" : "outline"}>{ev.status}</Badge>
        </div>
        <div className="flex items-center justify-center gap-6 py-2">
          <div className="flex-1 text-right text-lg font-bold">{ev.home}</div>
          <div className="font-mono text-2xl font-black tabular-nums">
            {live || ev.status === "FINISHED" ? `${ev.homeScore} : ${ev.awayScore}` : "vs"}
          </div>
          <div className="flex-1 text-left text-lg font-bold">{ev.away}</div>
        </div>
      </Card>

      {ev.markets.map((m) => (
        <Card key={m.id} className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-border bg-secondary/40 px-3 py-2">
            <span className="text-sm font-semibold">{m.name}</span>
            {m.status !== "OPEN" && <Badge variant="danger">Suspended</Badge>}
          </div>
          <div className="grid grid-cols-2 gap-1.5 p-2 sm:grid-cols-3">
            {m.selections.map((sel) => (
              <OddsButton
                key={sel.id}
                label={sel.name}
                odds={sel.odds}
                active={has(sel.id)}
                disabled={m.status !== "OPEN"}
                onClick={() =>
                  toggle({
                    selectionId: sel.id,
                    eventId: ev.id,
                    eventLabel,
                    marketName: m.name,
                    selectionName: sel.name,
                    odds: sel.odds,
                  })
                }
              />
            ))}
          </div>
        </Card>
      ))}
    </div>
  )
}
