"use client"

import useSWR, { mutate } from "swr"
import { useState } from "react"
import { Card, Skeleton, Badge, Button, Input, Select } from "@/components/ui/kit"
import { apiPost } from "@/lib/client/api"
import { useToasts } from "@/lib/client/stores"
import type { SupportMessage, SupportTicket, TicketStatus } from "@/lib/domain/types"

const NEXT: Record<TicketStatus, TicketStatus[]> = {
  OPEN: ["ASSIGNED", "IN_PROGRESS", "CLOSED"],
  ASSIGNED: ["IN_PROGRESS", "WAITING", "CLOSED"],
  IN_PROGRESS: ["WAITING", "RESOLVED", "CLOSED"],
  WAITING: ["IN_PROGRESS", "RESOLVED", "CLOSED"],
  RESOLVED: ["CLOSED", "IN_PROGRESS"],
  CLOSED: [],
}

export function TicketThread({ ticketId }: { ticketId: string }) {
  const { data, isLoading } = useSWR<{ ticket: SupportTicket; messages: SupportMessage[]; isStaff: boolean }>(
    `/api/support/${ticketId}`,
  )
  const push = useToasts((s) => s.push)
  const [reply, setReply] = useState("")
  const [busy, setBusy] = useState(false)

  async function send() {
    if (!reply.trim()) return
    setBusy(true)
    try {
      await apiPost(`/api/support/${ticketId}`, { message: reply })
      setReply("")
      mutate(`/api/support/${ticketId}`)
      push("Reply sent", "success")
    } catch (e) {
      push((e as Error).message, "error")
    } finally {
      setBusy(false)
    }
  }

  async function changeStatus(status: string) {
    try {
      await apiPost(`/api/support/${ticketId}`, { status })
      mutate(`/api/support/${ticketId}`)
      mutate((k) => typeof k === "string" && k.startsWith("/api/support"))
      push(`Status → ${status}`, "success")
    } catch (e) {
      push((e as Error).message, "error")
    }
  }

  if (isLoading) return <Skeleton className="h-64" />
  if (!data) return null
  const { ticket, messages, isStaff } = data

  return (
    <Card className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-border p-3">
        <div>
          <p className="text-sm font-bold">{ticket.subject}</p>
          <p className="text-xs text-muted-foreground">
            {ticket.customerName} · {ticket.category}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="default">{ticket.status}</Badge>
          {isStaff && NEXT[ticket.status].length > 0 && (
            <Select className="h-8 w-36" value="" onChange={(e) => e.target.value && changeStatus(e.target.value)}>
              <option value="">Move to…</option>
              {NEXT[ticket.status].map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Select>
          )}
        </div>
      </div>
      <div className="flex max-h-[360px] flex-1 flex-col gap-2 overflow-y-auto p-3">
        {messages.map((m) => (
          <div key={m.id} className="rounded border border-border bg-secondary/40 p-2">
            <div className="mb-0.5 flex items-center justify-between">
              <span className="text-xs font-semibold">{m.authorName}</span>
              <span className="text-[11px] text-muted-foreground">
                {new Date(m.createdAt).toLocaleString("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
            <p className="text-sm text-foreground/90">{m.body}</p>
            {m.internal && <Badge variant="warn" className="mt-1">Internal note</Badge>}
          </div>
        ))}
      </div>
      {ticket.status !== "CLOSED" && (
        <div className="flex gap-2 border-t border-border p-3">
          <Input
            value={reply}
            onChange={(e) => setReply(e.target.value)}
            placeholder="Type a reply…"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.nativeEvent.isComposing && e.keyCode !== 229) send()
            }}
          />
          <Button onClick={send} disabled={busy}>
            Send
          </Button>
        </div>
      )}
    </Card>
  )
}
