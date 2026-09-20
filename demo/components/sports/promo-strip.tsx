"use client"

import useSWR from "swr"
import { Skeleton } from "@/components/ui/kit"

interface Banner {
  id: string
  title: string
  subtitle: string
  theme: string
}

const THEME: Record<string, string> = {
  sports: "from-[var(--nav)] to-primary",
  casino: "from-[var(--chart-5)] to-primary",
  live: "from-[var(--live)] to-[var(--nav)]",
}

export function PromoStrip() {
  const { data, isLoading } = useSWR<{ banners: Banner[] }>("/api/promotions")
  if (isLoading) return <Skeleton className="h-28 w-full rounded-md" />
  const banners = data?.banners ?? []
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      {banners.map((b) => (
        <div
          key={b.id}
          className={`relative overflow-hidden rounded-md bg-gradient-to-br ${THEME[b.theme] ?? THEME.sports} p-4`}
        >
          <p className="text-sm font-bold text-white">{b.title}</p>
          <p className="mt-1 text-xs text-white/80">{b.subtitle}</p>
          <span className="mt-3 inline-block rounded bg-white/20 px-2 py-0.5 text-[10px] font-bold uppercase text-white">
            Demo credits
          </span>
        </div>
      ))}
    </div>
  )
}
