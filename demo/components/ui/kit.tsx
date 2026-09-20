"use client"

import { cn } from "@/lib/utils"
import type { ReactNode } from "react"

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: ReactNode
  variant?: "default" | "live" | "outline" | "success" | "warn" | "danger" | "muted"
  className?: string
}) {
  const styles: Record<string, string> = {
    default: "bg-primary/15 text-primary border-primary/30",
    live: "bg-[var(--live)]/15 text-[var(--live)] border-[var(--live)]/40",
    outline: "bg-transparent text-muted-foreground border-border",
    success: "bg-[var(--up)]/15 text-[var(--up)] border-[var(--up)]/40",
    warn: "bg-[var(--chart-3)]/15 text-[var(--chart-3)] border-[var(--chart-3)]/40",
    danger: "bg-destructive/15 text-destructive border-destructive/40",
    muted: "bg-muted text-muted-foreground border-border",
  }
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
        styles[variant],
        className,
      )}
    >
      {children}
    </span>
  )
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("rounded-md border border-border bg-card", className)}>{children}</div>
}

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={cn("inline-block size-4 animate-spin rounded-full border-2 border-muted-foreground/30 border-t-primary", className)}
      aria-label="Loading"
    />
  )
}

export function EmptyState({ title, hint, icon }: { title: string; hint?: string; icon?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-md border border-dashed border-border py-10 text-center">
      {icon && <div className="text-muted-foreground">{icon}</div>}
      <p className="text-sm font-medium text-foreground">{title}</p>
      {hint && <p className="max-w-xs text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded bg-muted/60", className)} />
}

const btnBase =
  "inline-flex items-center justify-center gap-1.5 rounded font-medium transition-colors disabled:pointer-events-none disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:ring-offset-background"

export function Button({
  children,
  variant = "primary",
  size = "md",
  className,
  ...props
}: {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "outline" | "success"
  size?: "sm" | "md" | "icon"
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const variants: Record<string, string> = {
    primary: "bg-primary text-primary-foreground hover:bg-primary/90",
    secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
    ghost: "bg-transparent text-foreground hover:bg-accent",
    danger: "bg-destructive text-white hover:bg-destructive/90",
    success: "bg-[var(--up)] text-black hover:bg-[var(--up)]/90",
    outline: "border border-border bg-transparent text-foreground hover:bg-accent",
  }
  const sizes: Record<string, string> = {
    sm: "h-7 px-2.5 text-xs",
    md: "h-9 px-3.5 text-sm",
    icon: "size-9",
  }
  return (
    <button className={cn(btnBase, variants[variant], sizes[size], className)} {...props}>
      {children}
    </button>
  )
}

export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-9 w-full rounded border border-input bg-background/60 px-3 text-sm text-foreground placeholder:text-muted-foreground focus-visible:border-primary focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
        className,
      )}
      {...props}
    />
  )
}

export function Select({ className, children, ...props }: React.SelectHTMLAttributes<HTMLSelectElement> & { children: ReactNode }) {
  return (
    <select
      className={cn(
        "h-9 w-full rounded border border-input bg-background/60 px-2.5 text-sm text-foreground focus-visible:border-primary focus-visible:outline-none",
        className,
      )}
      {...props}
    >
      {children}
    </select>
  )
}

export function OddsButton({
  label,
  odds,
  active,
  disabled,
  onClick,
}: {
  label: string
  odds: number
  active?: boolean
  disabled?: boolean
  onClick?: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "group flex min-w-0 flex-1 items-center justify-between gap-1 rounded border px-2 py-1.5 text-left transition-colors",
        active
          ? "border-primary bg-primary/20 text-primary"
          : "border-border bg-secondary/40 hover:border-primary/50 hover:bg-secondary",
        disabled && "cursor-not-allowed opacity-40",
      )}
    >
      <span className="truncate text-[11px] text-muted-foreground group-hover:text-foreground">{label}</span>
      <span className="font-mono text-xs font-semibold tabular-nums">{odds.toFixed(2)}</span>
    </button>
  )
}
