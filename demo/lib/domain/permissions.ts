export const PERMISSIONS = [
  "users.read",
  "users.update",
  "users.suspend",
  "users.unlock",
  "employees.manage",
  "roles.manage",
  "bets.read",
  "bets.create_mock",
  "bets.settle_mock",
  "sports.read",
  "sports.create",
  "sports.update",
  "sports.suspend_market",
  "odds.update",
  "casino.read",
  "casino.create",
  "casino.update",
  "promotions.create",
  "promotions.publish",
  "support.read",
  "support.respond",
  "risk.read",
  "risk.resolve",
  "ledger.read",
  "ledger.adjust_mock",
  "cms.read",
  "cms.publish",
  "analytics.read",
  "audit.read",
  "system.settings",
  "forum.moderate",
  "notifications.send_mock",
] as const

export type Permission = (typeof PERMISSIONS)[number]

export const ROLES = [
  "CUSTOMER",
  "CUSTOMER_SUPPORT",
  "SPORTS_OPERATOR",
  "CASINO_OPERATOR",
  "PROMOTION_MANAGER",
  "RISK_ANALYST",
  "CONTENT_EDITOR",
  "FINANCE_OPERATOR",
  "ADMIN",
] as const

export type RoleName = (typeof ROLES)[number]

export const ROLE_PERMISSIONS: Record<RoleName, Permission[]> = {
  CUSTOMER: ["bets.create_mock", "sports.read", "casino.read", "cms.read"],
  CUSTOMER_SUPPORT: ["users.read", "bets.read", "support.read", "support.respond", "ledger.read"],
  SPORTS_OPERATOR: [
    "sports.read",
    "sports.create",
    "sports.update",
    "sports.suspend_market",
    "odds.update",
    "bets.read",
    "bets.settle_mock",
  ],
  CASINO_OPERATOR: ["casino.read", "casino.create", "casino.update"],
  PROMOTION_MANAGER: ["promotions.create", "promotions.publish", "cms.read"],
  RISK_ANALYST: ["risk.read", "risk.resolve", "users.read", "users.suspend", "bets.read"],
  CONTENT_EDITOR: ["cms.read", "cms.publish"],
  FINANCE_OPERATOR: ["ledger.read", "ledger.adjust_mock", "bets.read", "analytics.read"],
  ADMIN: [...PERMISSIONS],
}

export const DEMO_ACCOUNTS: { email: string; role: RoleName; display: string }[] = [
  { email: "customer@example.test", role: "CUSTOMER", display: "Demo Customer" },
  { email: "support@example.test", role: "CUSTOMER_SUPPORT", display: "Support Agent" },
  { email: "sports@example.test", role: "SPORTS_OPERATOR", display: "Sports Operator" },
  { email: "casino@example.test", role: "CASINO_OPERATOR", display: "Casino Operator" },
  { email: "promo@example.test", role: "PROMOTION_MANAGER", display: "Promotion Manager" },
  { email: "risk@example.test", role: "RISK_ANALYST", display: "Risk Analyst" },
  { email: "finance@example.test", role: "FINANCE_OPERATOR", display: "Finance Operator" },
  { email: "content@example.test", role: "CONTENT_EDITOR", display: "Content Editor" },
  { email: "admin@example.test", role: "ADMIN", display: "System Admin" },
]

export const DEMO_PASSWORD = "DemoOnly123!"

export function permissionsForRoles(roles: RoleName[]): Permission[] {
  const set = new Set<Permission>()
  for (const r of roles) for (const p of ROLE_PERMISSIONS[r] ?? []) set.add(p)
  return [...set]
}

/** Which portal a role lands in. CUSTOMER uses the public sportsbook. */
export function portalForRoles(roles: RoleName[]): "customer" | "staff" {
  return roles.some((r) => r !== "CUSTOMER") ? "staff" : "customer"
}
