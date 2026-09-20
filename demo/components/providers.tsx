"use client"

import { useEffect, useRef, useState } from "react"
import { usePathname } from "next/navigation"
import { SWRConfig } from "swr"
import { fetcher } from "@/lib/client/api"
import { recoverOrCreateSession, trackEvent } from "@/lib/client/session"
import { Toaster } from "@/components/toaster"

export function Providers({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const lastTrackedPath = useRef<string | null>(null)
  const [sessionReady, setSessionReady] = useState(false)

  const hasMounted = useRef(false)

  useEffect(() => {
    if (hasMounted.current) return
    hasMounted.current = true

    void recoverOrCreateSession()
      .then(() => {
        setSessionReady(true)
        return trackEvent({ event_type: "session_start", page: pathname, action: "application_entry" })
      })
      .catch((error: unknown) => {
        console.warn("PULSYNC session integration unavailable", error)
      })
    // The session is initialized once for the application lifetime.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!sessionReady || lastTrackedPath.current === pathname) return
    lastTrackedPath.current = pathname
    void trackEvent({ event_type: "page_view", page: pathname, action: "navigation" }).catch((error: unknown) => {
      console.warn("PULSYNC page event unavailable", error)
    })
  }, [pathname, sessionReady])

  return (
    <SWRConfig value={{ fetcher, revalidateOnFocus: false, dedupingInterval: 2000 }}>
      {children}
      <Toaster />
    </SWRConfig>
  )
}
