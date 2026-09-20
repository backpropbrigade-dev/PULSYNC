"use client"

import useSWR from "swr"
import { useState } from "react"
import { EventRow, type EventDto } from "./event-row"
import { Card, Skeleton, EmptyState, Badge } from "@/components/ui/kit"
import { cn } from "@/lib/utils"
import { CalendarX } from "lucide-react"

const DAYS = [
  { key: "today", label: "Today" },
  { key: "tomorrow", label: "Tomorrow" },
  { key: "all", label: "All" },
]

export function SportFeed({ sport, live = false }: { sport?: string; live?: boolean }) {
  const [day, setDay] = useState("all")
  const status = live ? "live" : ""
  const key = `/api/events?sport=${sport ?? "all"}&day=${day}${status ? `&status=${status}` : ""}`
  const { data, isLoading } = useSWR<{ events: EventDto[]; total: number }>(key, {
    refreshInterval: 5000,
  })

  // group by competition
  const groups: Record<string, EventDto[]> = {}
  for (const ev of data?.events ?? []) {
    const g = ev.competition?.name ?? "Other"
    ;(groups[g] ??= []).push(ev)
  }

  return (
    <div className="flex flex-col gap-3">
      {!live && (
        <div className="flex items-center gap-1 rounded-md border border-border bg-card p-1">
          {DAYS.map((d) => (
            <button
              key={d.key}
              onClick={() => setDay(d.key)}
              className={cn(
                "rounded px-3 py-1.5 text-sm font-semibold transition-colors",
                day === d.key ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent",
              )}
            >
              {d.label}
            </button>
          ))}
          <span className="ml-auto pr-2 text-xs text-muted-foreground">{data?.total ?? 0} events</span>
        </div>
      )}

      {isLoading && (
        <Card className="p-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="mb-2 h-12" />
          ))}
        </Card>
      )}

      {!isLoading && (data?.events.length ?? 0) === 0 && (
        <EmptyState
          icon={<CalendarX className="size-8" />}
          title="No events available"
          hint="Try a different sport or day filter. This is a mock feed with deterministic seed data."
        />
      )}

      {Object.entries(groups).map(([comp, evs]) => (
        <Card key={comp} className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-border bg-secondary/40 px-3 py-2">
            <span className="text-xs font-bold uppercase tracking-wide">{comp}</span>
            <div className="flex items-center gap-3 text-[11px] font-semibold text-muted-foreground">
              <span className="w-[70px] text-center sm:w-[82px]">1</span>
              <span className="w-[70px] text-center sm:w-[82px]">X</span>
              <span className="hidden w-[70px] text-center sm:block sm:w-[82px]">2</span>
            </div>
          </div>
          <div>
            {evs.map((ev) => (
              <EventRow key={ev.id} ev={ev} />
            ))}
          </div>
        </Card>
      ))}
    </div>
  )
}
