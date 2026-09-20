"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useAuth } from "@/lib/client/auth"
import { apiPost } from "@/lib/client/api"
import { useToasts } from "@/lib/client/stores"
import { DemoBanner } from "@/components/shell/demo-banner"
import { Spinner, Badge } from "@/components/ui/kit"
import { cn } from "@/lib/utils"
import type { Permission } from "@/lib/domain/permissions"
import {
  BarChart3,
  Users,
  ScrollText,
  Settings,
  Trophy,
  Receipt,
  Megaphone,
  MessageSquare,
  TriangleAlert,
  DollarSign,
  LogOut,
  ExternalLink,
  type LucideIcon,
} from "lucide-react"
import { useEffect } from "react"

interface NavItem {
  href: string
  label: string
  icon: LucideIcon
  perm?: Permission
}

const NAV: NavItem[] = [
  { href: "/portal", label: "Overview", icon: BarChart3 },
  { href: "/portal/users", label: "Users", icon: Users, perm: "users.read" },
  { href: "/portal/sports", label: "Sports Ops", icon: Trophy, perm: "sports.update" },
  { href: "/portal/bets", label: "Bets", icon: Receipt, perm: "bets.read" },
  { href: "/portal/promotions", label: "Promotions", icon: Megaphone, perm: "promotions.create" },
  { href: "/portal/support", label: "Support Queue", icon: MessageSquare, perm: "support.read" },
  { href: "/portal/risk", label: "Risk", icon: TriangleAlert, perm: "risk.read" },
  { href: "/portal/ledger", label: "Ledger", icon: DollarSign, perm: "ledger.read" },
  { href: "/portal/analytics", label: "Analytics", icon: BarChart3, perm: "analytics.read" },
  { href: "/portal/audit", label: "Audit Log", icon: ScrollText, perm: "audit.read" },
  { href: "/portal/system", label: "System", icon: Settings, perm: "system.settings" },
]

export function PortalShell({ children }: { children: React.ReactNode }) {
  const { user, portal, isLoading, can, refresh } = useAuth()
  const pathname = usePathname()
  const router = useRouter()
  const push = useToasts((s) => s.push)

  useEffect(() => {
    if (!isLoading && (!user || portal !== "staff")) router.push("/login")
  }, [isLoading, user, portal, router])

  async function logout() {
    await apiPost("/api/auth/logout")
    await refresh()
    router.push("/login")
  }

  if (isLoading || !user)
    return (
      <div className="grid min-h-screen place-items-center bg-background">
        <Spinner className="size-6" />
      </div>
    )

  const visible = NAV.filter((n) => !n.perm || can(n.perm))

  return (
    <div className="min-h-screen bg-background text-foreground">
      <DemoBanner />
      <div className="flex">
        <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-border bg-sidebar md:flex">
          <div className="flex items-center gap-2 border-b border-border px-4 py-3">
            <span className="grid size-8 place-items-center rounded bg-[var(--nav)] font-mono text-sm font-black text-white">
              NX
            </span>
            <div>
              <p className="text-sm font-bold">Staff Portal</p>
              <p className="text-[10px] text-muted-foreground">DEMO</p>
            </div>
          </div>
          <nav className="flex-1 overflow-y-auto p-2">
            {visible.map((n) => {
              const active = pathname === n.href
              return (
                <Link
                  key={n.href}
                  href={n.href}
                  className={cn(
                    "mb-0.5 flex items-center gap-2 rounded px-2.5 py-2 text-sm transition-colors",
                    active ? "bg-primary/15 font-semibold text-primary" : "text-foreground/80 hover:bg-accent",
                  )}
                >
                  <n.icon className="size-4" />
                  {n.label}
                </Link>
              )
            })}
          </nav>
          <div className="border-t border-border p-2">
            <div className="mb-2 px-2">
              <p className="truncate text-xs font-semibold">{user.displayName}</p>
              <Badge>{user.roles[0]}</Badge>
            </div>
            <Link href="/" className="mb-1 flex items-center gap-2 rounded px-2.5 py-1.5 text-sm text-foreground/80 hover:bg-accent">
              <ExternalLink className="size-4" /> Customer site
            </Link>
            <button onClick={logout} className="flex w-full items-center gap-2 rounded px-2.5 py-1.5 text-sm text-foreground/80 hover:bg-accent">
              <LogOut className="size-4" /> Log out
            </button>
          </div>
        </aside>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 overflow-x-auto border-b border-border bg-sidebar px-2 py-2 md:hidden">
            {visible.map((n) => (
              <Link
                key={n.href}
                href={n.href}
                className={cn(
                  "whitespace-nowrap rounded px-2.5 py-1 text-xs font-semibold",
                  pathname === n.href ? "bg-primary/15 text-primary" : "text-foreground/80",
                )}
              >
                {n.label}
              </Link>
            ))}
          </div>
          <main className="mx-auto max-w-6xl p-4">{children}</main>
        </div>
      </div>
    </div>
  )
}
