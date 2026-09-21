import { NextResponse } from "next/server"
import { getCurrentUser, userHasPermission } from "./session"
import { getDb, nextId } from "./store"
import type { Permission } from "@/lib/domain/permissions"
import type { User } from "@/lib/domain/types"

export function ok(data: unknown, init?: number) {
  return NextResponse.json(data, { status: init ?? 200 })
}
export function err(message: string, status = 400) {
  return NextResponse.json({ error: message }, { status })
}

export async function requireUser(): Promise<{ user: User } | NextResponse> {
  const user = await getCurrentUser()
  if (!user) return err("Not authenticated", 401)
  if (user.status !== "ACTIVE") return err("Account is not active", 403)
  return { user }
}

export async function requirePermission(perm: Permission): Promise<{ user: User } | NextResponse> {
  const res = await requireUser()
  if (res instanceof NextResponse) return res
  if (!userHasPermission(res.user, perm)) return err("Forbidden: missing permission " + perm, 403)
  return res
}

export function audit(actor: User, action: string, resourceType: string, resourceId: string, reason: string) {
  const db = getDb()
  db.audit.unshift({
    id: nextId("aud"),
    actorId: actor.id,
    actorRole: actor.roles[0] ?? "UNKNOWN",
    action,
    resourceType,
    resourceId,
    reason,
    createdAt: new Date().toISOString(),
  })
}
