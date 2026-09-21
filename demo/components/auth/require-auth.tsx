"use client"

import { useAuth } from "@/lib/client/auth"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Spinner, Card, Button } from "@/components/ui/kit"
import type { Permission } from "@/lib/domain/permissions"
import Link from "next/link"
import { Lock } from "lucide-react"

export function RequireAuth({
  children,
  permission,
  redirect = true,
}: {
  children: React.ReactNode
  permission?: Permission
  redirect?: boolean
}) {
  const { user, isLoading, can } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user && redirect) router.push("/login")
  }, [isLoading, user, redirect, router])

  if (isLoading)
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner className="size-6" />
      </div>
    )

  if (!user)
    return (
      <Card className="mx-auto max-w-md p-6 text-center">
        <Lock className="mx-auto mb-2 size-8 text-muted-foreground" />
        <h2 className="text-base font-bold">Sign in required</h2>
        <p className="mb-4 mt-1 text-sm text-muted-foreground">Please log in with a demo account to continue.</p>
        <Link href="/login">
          <Button>Go to login</Button>
        </Link>
      </Card>
    )

  if (permission && !can(permission))
    return (
      <Card className="mx-auto max-w-md p-6 text-center">
        <Lock className="mx-auto mb-2 size-8 text-destructive" />
        <h2 className="text-base font-bold">Access denied</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Your role does not have the <code className="font-mono text-xs">{permission}</code> permission.
        </p>
      </Card>
    )

  return <>{children}</>
}
