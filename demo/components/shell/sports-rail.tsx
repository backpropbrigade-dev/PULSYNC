"use client"

import useSWR from "swr"
import Link from "next/link"
import { usePathname, useSearchParams } from "next/navigation"
import { Skeleton, Badge } from "@/components/ui/kit"
import { cn } from "@/lib/utils"
import { Trophy, Zap, Star, Gift, type LucideIcon } from "lucide-react"

interface SportRow {
  id: string
  slug: string
  name: string
  eventCount: number
  liveCount: number
}

const ICONS: Record<string, LucideIcon> = {
  football: Trophy,
}

export function SportsRail() {
  const { data, isLoading } = useSWR<{ sports: SportRow[] }>("/api/sports")
  const params = useSearchParams()
  const pathname = usePathname()
  const activeSport = params.get("sport") ?? "all"

  return (
    <aside className="flex w-full flex-col gap-4">
      <nav className="rounded-md border border-border bg-card">
        <div className="border-b border-border px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
          Recommended
        </div>
        <div className="flex flex-col p-1">
          <RailLink href="/sport" icon={Star} label="Top offer" active={pathname === "/sport" && activeSport === "all"} />
          <RailLink href="/live" icon={Zap} label="Live now" />
          <RailLink href="/promotions" icon={Gift} label="Promotions" />
        </div>
      </nav>

      <nav className="rounded-md border border-border bg-card">
        <div className="border-b border-border px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
          Sports
        </div>
        <div className="flex max-h-[520px] flex-col overflow-y-auto p-1">
          {isLoading &&
            Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="mx-1 my-0.5 h-8" />)}
          {data?.sports.map((s) => {
            const Icon = ICONS[s.slug] ?? Trophy
            const active = pathname.startsWith("/sport") && activeSport === s.slug
            return (
              <Link
                key={s.id}
                href={`/sport?sport=${s.slug}`}
                className={cn(
                  "flex items-center gap-2 rounded px-2.5 py-1.5 text-sm transition-colors hover:bg-accent",
                  active ? "bg-accent font-semibold text-foreground" : "text-foreground/80",
                )}
              >
                <Icon className="size-4 shrink-0 text-muted-foreground" />
                <span className="flex-1 truncate">{s.name}</span>
                {s.liveCount > 0 && <Badge variant="live">{s.liveCount}</Badge>}
                <span className="text-[11px] tabular-nums text-muted-foreground">{s.eventCount}</span>
              </Link>
            )
          })}
        </div>
      </nav>
    </aside>
  )
}

function RailLink({ href, icon: Icon, label, active }: { href: string; icon: LucideIcon; label: string; active?: boolean }) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-2 rounded px-2.5 py-1.5 text-sm transition-colors hover:bg-accent",
        active ? "bg-accent font-semibold" : "text-foreground/80",
      )}
    >
      <Icon className="size-4 text-primary" />
      {label}
    </Link>
  )
}
