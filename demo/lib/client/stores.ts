"use client"

import { create } from "zustand"

export interface BetSlipItem {
  selectionId: string
  eventId: string
  eventLabel: string
  marketName: string
  selectionName: string
  odds: number
}

interface BetSlipState {
  items: BetSlipItem[]
  stake: number
  open: boolean
  add: (item: BetSlipItem) => void
  remove: (selectionId: string) => void
  toggle: (item: BetSlipItem) => void
  clear: () => void
  setStake: (n: number) => void
  setOpen: (v: boolean) => void
  has: (selectionId: string) => boolean
}

export const useBetSlip = create<BetSlipState>((set, get) => ({
  items: [],
  stake: 10,
  open: false,
  add: (item) =>
    set((s) => {
      if (s.items.some((i) => i.selectionId === item.selectionId)) return s
      // one selection per event
      const filtered = s.items.filter((i) => i.eventId !== item.eventId)
      return { items: [...filtered, item], open: true }
    }),
  remove: (selectionId) => set((s) => ({ items: s.items.filter((i) => i.selectionId !== selectionId) })),
  toggle: (item) => {
    const has = get().items.some((i) => i.selectionId === item.selectionId)
    if (has) get().remove(item.selectionId)
    else get().add(item)
  },
  clear: () => set({ items: [], stake: 10 }),
  setStake: (n) => set({ stake: n }),
  setOpen: (v) => set({ open: v }),
  has: (selectionId) => get().items.some((i) => i.selectionId === selectionId),
}))

interface ToastItem {
  id: string
  message: string
  variant: "success" | "error" | "info"
}
interface ToastState {
  toasts: ToastItem[]
  push: (message: string, variant?: ToastItem["variant"]) => void
  dismiss: (id: string) => void
}
export const useToasts = create<ToastState>((set) => ({
  toasts: [],
  push: (message, variant = "info") => {
    const id = Math.random().toString(36).slice(2)
    set((s) => ({ toasts: [...s.toasts, { id, message, variant }] }))
    setTimeout(() => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), 3500)
  },
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))
