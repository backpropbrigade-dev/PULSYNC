import { AlertTriangle } from "lucide-react"

export function DemoBanner() {
  return (
    <div className="flex items-center justify-center gap-2 bg-[var(--chart-3)]/15 px-3 py-1 text-center text-[11px] font-semibold uppercase tracking-wide text-[var(--chart-3)]">
      <AlertTriangle className="size-3" />
      Demo / Mock Environment — DEMO CREDITS only. No real betting, payments, or data.
    </div>
  )
}
