"use client"

import { useToasts } from "@/lib/client/stores"
import { CheckCircle2, Info, XCircle } from "lucide-react"
import { cn } from "@/lib/utils"

export function Toaster() {
  const { toasts, dismiss } = useToasts()
  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-full max-w-xs flex-col gap-2">
      {toasts.map((t) => (
        <button
          key={t.id}
          onClick={() => dismiss(t.id)}
          className={cn(
            "pointer-events-auto flex items-start gap-2 rounded-md border p-3 text-left text-sm shadow-lg backdrop-blur",
            t.variant === "success" && "border-[var(--up)]/40 bg-card text-foreground",
            t.variant === "error" && "border-destructive/40 bg-card text-foreground",
            t.variant === "info" && "border-border bg-card text-foreground",
          )}
        >
          {t.variant === "success" && <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-[var(--up)]" />}
          {t.variant === "error" && <XCircle className="mt-0.5 size-4 shrink-0 text-destructive" />}
          {t.variant === "info" && <Info className="mt-0.5 size-4 shrink-0 text-primary" />}
          <span className="leading-snug">{t.message}</span>
        </button>
      ))}
    </div>
  )
}
