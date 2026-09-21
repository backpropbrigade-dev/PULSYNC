"use client"

import { type ReactNode, Suspense } from "react"
import { TopNav } from "./top-nav"
import { DemoBanner } from "./demo-banner"
import { SportsRail } from "./sports-rail"
import { BetSlip } from "./bet-slip"

export function CustomerShell({
  children,
  showRail = true,
  showSlip = true,
}: {
  children: ReactNode
  showRail?: boolean
  showSlip?: boolean
}) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <DemoBanner />
      <TopNav />
      <div className="mx-auto max-w-[1600px] px-3 py-4">
        <div className="flex gap-4">
          {showRail && (
            <div className="hidden w-56 shrink-0 lg:block xl:w-64">
              <Suspense fallback={<div className="h-full rounded-md bg-card" />}>
                <SportsRail />
              </Suspense>
            </div>
          )}
          <main className="min-w-0 flex-1">{children}</main>
          {showSlip && (
            <div className="hidden w-[300px] shrink-0 lg:block">
              <BetSlip variant="sidebar" />
            </div>
          )}
        </div>
      </div>
      {showSlip && <BetSlip variant="drawer" />}
    </div>
  )
}
