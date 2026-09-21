"use client"

import { useState } from "react"
import { useBetSlip, useToasts } from "@/lib/client/stores"
import { useAuth } from "@/lib/client/auth"
import { apiPost, fmtCredits } from "@/lib/client/api"
import { Button, Input, Spinner } from "@/components/ui/kit"
import { cn } from "@/lib/utils"
import { Receipt, Trash2, X } from "lucide-react"
import Link from "next/link"
import { mutate } from "swr"

export function BetSlip({ variant = "sidebar" }: { variant?: "sidebar" | "drawer" }) {
  const { items, stake, setStake, remove, clear, open, setOpen } = useBetSlip()
  const { user, refresh } = useAuth()
  const push = useToasts((s) => s.push)
  const [submitting, setSubmitting] = useState(false)

  const combined = items.reduce((acc, i) => acc * i.odds, 1)
  const potential = stake > 0 ? stake * combined : 0
  const isMulti = items.length > 1

  async function submit() {
    if (!user) {
      push("Log in to place a demo bet", "error")
      return
    }
    if (items.length === 0 || stake <= 0) return
    setSubmitting(true)
    try {
      const res = await apiPost("/api/bets", { selectionIds: items.map((i) => i.selectionId), stake })
      push(`Bet ${res.bet.ticketCode} placed — ${fmtCredits(res.bet.potentialPayout)} potential`, "success")
      clear()
      setOpen(false)
      await refresh()
      mutate("/api/wallet")
      mutate((key) => typeof key === "string" && key.startsWith("/api/bets"))
    } catch (e) {
      push((e as Error).message, "error")
    } finally {
      setSubmitting(false)
    }
  }

  const body = (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <div className="flex items-center gap-2 text-sm font-bold">
          <Receipt className="size-4 text-primary" />
          Bet Slip
          {items.length > 0 && (
            <span className="grid size-5 place-items-center rounded-full bg-primary text-[11px] text-primary-foreground">
              {items.length}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          {items.length > 0 && (
            <button onClick={clear} className="rounded p-1 text-muted-foreground hover:text-destructive" aria-label="Clear slip">
              <Trash2 className="size-4" />
            </button>
          )}
          {variant === "drawer" && (
            <button onClick={() => setOpen(false)} className="rounded p-1 text-muted-foreground lg:hidden" aria-label="Close">
              <X className="size-4" />
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
            <Receipt className="size-8 text-muted-foreground/40" />
            <p className="text-sm font-medium">Your slip is empty</p>
            <p className="max-w-[200px] text-xs text-muted-foreground">
              Tap odds on any event to add a selection. DEMO CREDITS only.
            </p>
          </div>
        ) : (
          <ul className="flex flex-col gap-2">
            {items.map((i) => (
              <li key={i.selectionId} className="rounded border border-border bg-secondary/40 p-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="truncate text-xs font-semibold">{i.selectionName}</p>
                    <p className="truncate text-[11px] text-muted-foreground">{i.marketName}</p>
                    <p className="truncate text-[11px] text-muted-foreground">{i.eventLabel}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="font-mono text-xs font-bold tabular-nums text-primary">{i.odds.toFixed(2)}</span>
                    <button
                      onClick={() => remove(i.selectionId)}
                      className="text-muted-foreground hover:text-destructive"
                      aria-label="Remove selection"
                    >
                      <X className="size-3.5" />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {items.length > 0 && (
        <div className="border-t border-border p-3">
          <div className="mb-2 flex items-center justify-between text-xs">
            <span className="text-muted-foreground">{isMulti ? "Multi" : "Single"} · Combined odds</span>
            <span className="font-mono font-bold tabular-nums">{combined.toFixed(2)}</span>
          </div>
          <label className="mb-1 block text-[11px] font-semibold uppercase text-muted-foreground">Stake (DEMO)</label>
          <div className="mb-2 flex gap-1">
            <Input
              type="number"
              min={1}
              value={stake}
              onChange={(e) => setStake(Number(e.target.value))}
              className="font-mono"
            />
            {[10, 25, 50].map((v) => (
              <Button key={v} variant="outline" size="sm" onClick={() => setStake(v)} className="shrink-0">
                {v}
              </Button>
            ))}
          </div>
          <div className="mb-3 flex items-center justify-between rounded bg-secondary/60 px-2 py-1.5 text-sm">
            <span className="text-muted-foreground">Potential return</span>
            <span className="font-mono font-bold tabular-nums text-[var(--up)]">{fmtCredits(potential)}</span>
          </div>
          {user ? (
            <Button onClick={submit} disabled={submitting || stake <= 0} className="w-full">
              {submitting ? <Spinner className="border-primary-foreground/40 border-t-primary-foreground" /> : "Place Demo Bet"}
            </Button>
          ) : (
            <Link href="/login">
              <Button className="w-full">Log in to bet</Button>
            </Link>
          )}
        </div>
      )}
    </div>
  )

  if (variant === "sidebar") {
    return (
      <div className="sticky top-24 hidden h-[calc(100vh-7rem)] rounded-md border border-border bg-card lg:block">{body}</div>
    )
  }

  return (
    <div
      className={cn(
        "fixed inset-0 z-50 lg:hidden",
        open ? "pointer-events-auto" : "pointer-events-none",
      )}
      aria-hidden={!open}
    >
      <div
        className={cn("absolute inset-0 bg-black/60 transition-opacity", open ? "opacity-100" : "opacity-0")}
        onClick={() => setOpen(false)}
      />
      <div
        className={cn(
          "absolute inset-x-0 bottom-0 max-h-[85vh] rounded-t-xl border-t border-border bg-card transition-transform",
          open ? "translate-y-0" : "translate-y-full",
        )}
      >
        {body}
      </div>
    </div>
  )
}
