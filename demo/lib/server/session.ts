import { cookies } from "next/headers"
import { getDb, nextId } from "./store"
import type { User } from "@/lib/domain/types"
import { permissionsForRoles, type Permission } from "@/lib/domain/permissions"

const COOKIE = "psk_session"

export async function createSession(userId: string): Promise<string> {
  const db = getDb()
  const token = nextId("sess") + Math.random().toString(36).slice(2)
  db.sessions.set(token, userId)
  const jar = await cookies()
  jar.set(COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: true,
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  })
  return token
}

export async function destroySession() {
  const db = getDb()
  const jar = await cookies()
  const token = jar.get(COOKIE)?.value
  if (token) db.sessions.delete(token)
  jar.delete(COOKIE)
}

export async function getCurrentUser(): Promise<User | null> {
  const db = getDb()
  const jar = await cookies()
  const token = jar.get(COOKIE)?.value
  if (!token) return null
  const userId = db.sessions.get(token)
  if (!userId) return null
  return db.users.find((u) => u.id === userId) ?? null
}

export function userPermissions(user: User): Permission[] {
  return permissionsForRoles(user.roles)
}

export function userHasPermission(user: User, perm: Permission): boolean {
  return userPermissions(user).includes(perm)
}
