"use client"

import useSWR from "swr"
import { fetcher } from "./api"
import type { Permission, RoleName } from "@/lib/domain/permissions"

export interface CurrentUser {
  id: string
  email: string
  displayName: string
  roles: RoleName[]
  status: string
  city: string
}

export interface MeResponse {
  user: CurrentUser | null
  permissions?: Permission[]
  portal?: "customer" | "staff"
  wallet?: { available: number; bonus: number; currency: string }
}

export function useAuth() {
  const { data, error, isLoading, mutate } = useSWR<MeResponse>("/api/auth/me", fetcher, {
    revalidateOnFocus: false,
  })
  const user = data?.user ?? null
  const permissions = data?.permissions ?? []
  return {
    user,
    permissions,
    portal: data?.portal,
    wallet: data?.wallet,
    isLoading,
    error,
    can: (p: Permission) => permissions.includes(p),
    refresh: mutate,
  }
}
