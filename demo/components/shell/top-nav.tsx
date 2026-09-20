"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useAuth } from "@/lib/client/auth"
import { apiPost, fmtCredits } from "@/lib/client/api"
import { useBetSlip, useToasts } from "@/lib/client/stores"
import { Button } from "@/components/ui/kit"
import { cn } from "@/lib/utils"
import { LogOut, Receipt, ShieldCheck, User2, Wallet } from "lucide-react"

const PRIMARY = [
  { href: "/sport", label: "Sport" },
  { href: "/live", label: "Live" },
  { href: "/casino", label: "Casino" },
  { href: "/promotions", label: "Promotions" },
  { href: "/support", label: "Support" },
]

export function TopNav() {
  const { user, wallet, portal, refresh } = useAuth()
  const pathname = usePathname()
  const router = useRouter()
  const { items, setOpen } = useBetSlip()
  const push = useToasts((s) => s.push)

  async function logout() {
    await apiPost("/api/auth/logout")
    await refresh()
    push("Signed out", "info")
    router.push("/login")
  }

  return (
    <header className="sticky top-0 z-40 border-b border-border">
      <div className="bg-[var(--nav)]">
        <div className="mx-auto flex h-14 max-w-[1600px] items-center gap-4 px-3">
          <Link href="/" className="flex items-center gap-2">
            <span className="grid size-8 place-items-center rounded bg-white font-mono text-sm font-black text-[var(--nav)]">
              PS
            </span>
            <span className="hidden text-sm font-bold uppercase tracking-wider text-white sm:block">PulSync</span>
          </Link>
          <nav className="hidden items-center gap-1 md:flex">
            {PRIMARY.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "rounded px-3 py-1.5 text-sm font-semibold text-white/80 transition-colors hover:bg-white/10 hover:text-white",
                  pathname.startsWith(item.href) && "bg-white/15 text-white",
                )}
              >
                {item.label}
              </Link>
            ))}
            {portal === "staff" && (
              <Link
                href="/portal"
                className={cn(
                  "flex items-center gap-1 rounded px-3 py-1.5 text-sm font-semibold text-white/80 hover:bg-white/10 hover:text-white",
                  pathname.startsWith("/portal") && "bg-white/15 text-white",
                )}
              >
                <ShieldCheck className="size-3.5" /> Staff
              </Link>
            )}
          </nav>
          <div className="ml-auto flex items-center gap-2">
            {user ? (
              <>
                <Link
                  href="/wallet"
                  className="hidden items-center gap-1.5 rounded bg-white/10 px-2.5 py-1.5 text-sm font-semibold text-white sm:flex"
                >
                  <Wallet className="size-3.5" />
                  <span className="font-mono tabular-nums">{fmtCredits(wallet?.available)}</span>
                  <span className="text-[10px] text-white/60">DEMO</span>
                </Link>
                <button
                  onClick={() => setOpen(true)}
                  className="relative flex items-center gap-1 rounded bg-white/10 px-2.5 py-1.5 text-sm font-semibold text-white lg:hidden"
                  aria-label="Open bet slip"
                >
                  <Receipt className="size-4" />
                  {items.length > 0 && (
                    <span className="absolute -right-1 -top-1 grid size-4 place-items-center rounded-full bg-[var(--live)] text-[10px] text-white">
                      {items.length}
                    </span>
                  )}
                </button>
                <Link
                  href="/profile"
                  className="grid size-8 place-items-center rounded-full bg-white/15 text-white"
                  aria-label="Profile"
                >
                  <User2 className="size-4" />
                </Link>
                <button
                  onClick={logout}
                  className="grid size-8 place-items-center rounded text-white/80 hover:bg-white/10 hover:text-white"
                  aria-label="Log out"
                >
                  <LogOut className="size-4" />
                </button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="secondary" size="sm">
                    Log in
                  </Button>
                </Link>
                <Link href="/login" className="hidden sm:block">
                  <Button size="sm">Register (Demo)</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
      <div className="border-t border-white/10 bg-[var(--nav)]/90">
        <div className="mx-auto flex h-8 max-w-[1600px] items-center gap-1 overflow-x-auto px-3 md:hidden">
          {PRIMARY.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "whitespace-nowrap rounded px-2.5 py-1 text-xs font-semibold text-white/80",
                pathname.startsWith(item.href) && "bg-white/15 text-white",
              )}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </header>
  )
}
