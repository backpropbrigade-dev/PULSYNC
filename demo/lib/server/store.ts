import { DEMO_ACCOUNTS, DEMO_PASSWORD, ROLES } from "@/lib/domain/permissions"
import type {
  AuditLog,
  Banner,
  Bet,
  CasinoGame,
  CMSContent,
  Competition,
  Event,
  FeatureFlag,
  LedgerEntry,
  Market,
  Notification,
  Participant,
  Promotion,
  RiskAlert,
  Selection,
  Sport,
  SupportMessage,
  SupportTicket,
  SystemSetting,
  Transaction,
  User,
  Wallet,
} from "@/lib/domain/types"

// ---- deterministic RNG (mulberry32) ----
function mulberry32(seed: number) {
  let a = seed >>> 0
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

export interface Db {
  users: User[]
  wallets: Wallet[]
  transactions: Transaction[]
  ledger: LedgerEntry[]
  sports: Sport[]
  competitions: Competition[]
  participants: Participant[]
  events: Event[]
  markets: Market[]
  selections: Selection[]
  bets: Bet[]
  casino: CasinoGame[]
  promotions: Promotion[]
  banners: Banner[]
  cms: CMSContent[]
  tickets: SupportTicket[]
  messages: SupportMessage[]
  risk: RiskAlert[]
  notifications: Notification[]
  audit: AuditLog[]
  flags: FeatureFlag[]
  settings: SystemSetting[]
  sessions: Map<string, string> // token -> userId
  seq: number
  lastTick: number
}

const SPORTS_DEF: [string, string][] = [
  ["football", "Football"],
  ["basketball", "Basketball"],
  ["tennis", "Tennis"],
  ["handball", "Handball"],
  ["ice-hockey", "Ice Hockey"],
  ["volleyball", "Volleyball"],
  ["american-football", "American Football"],
  ["boxing", "Boxing"],
  ["motor-sports", "Motor Sports"],
  ["esports", "Esports"],
]

const MARKET_DEFS: [string, string[]][] = [
  ["1X2", ["1", "X", "2"]],
  ["Double Chance", ["1X", "12", "X2"]],
  ["Over/Under 2.5", ["Over 2.5", "Under 2.5"]],
  ["Both Teams To Score", ["Yes", "No"]],
  ["Asian Handicap", ["Home -0.5", "Away +0.5"]],
  ["Draw No Bet", ["Home", "Away"]],
]

const CASINO_CATS = ["Jackpots", "New Games", "Popular", "Game Shows", "Table Games", "Big Wins"]
const CITIES = ["Harbor City", "Northgate", "Riverbend", "Old Town", "Silverport", "Lakeside", "Fairhaven"]
const FIRST = ["Ana", "Luka", "Mia", "Ivan", "Sara", "Marko", "Petra", "Nikola", "Eva", "Filip", "Lea", "Toni"]
const LAST = ["Kovac", "Horvat", "Novak", "Maric", "Juric", "Babic", "Vukovic", "Peric", "Blazevic", "Kralj"]

let ID = 0
function nid(prefix: string) {
  ID += 1
  return `${prefix}_${ID.toString(36)}`
}
function round2(n: number) {
  return Math.round(n * 100) / 100
}

export function buildDb(): Db {
  ID = 0
  const rnd = mulberry32(42)
  const pick = <T,>(arr: T[]) => arr[Math.floor(rnd() * arr.length)]
  const now = Date.now()
  const db: Db = {
    users: [],
    wallets: [],
    transactions: [],
    ledger: [],
    sports: [],
    competitions: [],
    participants: [],
    events: [],
    markets: [],
    selections: [],
    bets: [],
    casino: [],
    promotions: [],
    banners: [],
    cms: [],
    tickets: [],
    messages: [],
    risk: [],
    notifications: [],
    audit: [],
    flags: [],
    settings: [],
    sessions: new Map(),
    seq: 1,
    lastTick: now,
  }

  const N = { customers: 24, employees: 12, competitions: 16, events: 48, casino: 48, promotions: 8, tickets: 18, bets: 60, notifications: 40, audit: 30 }

  // demo accounts
  const demoUsers: Record<string, User> = {}
  for (const acc of DEMO_ACCOUNTS) {
    const u: User = {
      id: nid("usr"),
      email: acc.email,
      password: DEMO_PASSWORD,
      displayName: acc.display,
      roles: [acc.role],
      status: "ACTIVE",
      city: "Harbor City",
      isDemoSeed: true,
      createdAt: new Date(now - 90 * 864e5).toISOString(),
    }
    db.users.push(u)
    demoUsers[acc.email] = u
    if (acc.role === "CUSTOMER") db.wallets.push({ userId: u.id, available: 2500, bonus: 50 })
    else db.wallets.push({ userId: u.id, available: 0, bonus: 0 })
  }

  const customers: User[] = [demoUsers["customer@example.test"]]
  for (let i = 0; i < N.customers - 1; i++) {
    const u: User = {
      id: nid("usr"),
      email: `customer${String(i).padStart(4, "0")}@example.test`,
      password: DEMO_PASSWORD,
      displayName: `${pick(FIRST)} ${pick(LAST)}`,
      roles: ["CUSTOMER"],
      status: i % 13 === 0 ? "SUSPENDED" : "ACTIVE",
      city: pick(CITIES),
      isDemoSeed: true,
      createdAt: new Date(now - Math.floor(rnd() * 120) * 864e5).toISOString(),
    }
    db.users.push(u)
    db.wallets.push({ userId: u.id, available: 200 + ((i * 17) % 1800), bonus: 10 })
    customers.push(u)
  }

  const roleCycle = ROLES.filter((r) => r !== "CUSTOMER")
  for (let i = 0; i < N.employees; i++) {
    const rname = roleCycle[i % roleCycle.length]
    const u: User = {
      id: nid("usr"),
      email: `employee${String(i).padStart(3, "0")}@example.test`,
      password: DEMO_PASSWORD,
      displayName: `${pick(FIRST)} ${pick(LAST)}`,
      roles: [rname],
      status: "ACTIVE",
      city: pick(CITIES),
      isDemoSeed: true,
      createdAt: new Date(now - Math.floor(rnd() * 200) * 864e5).toISOString(),
    }
    db.users.push(u)
    db.wallets.push({ userId: u.id, available: 0, bonus: 0 })
  }

  // sports / competitions / participants
  SPORTS_DEF.forEach(([slug, name], i) => db.sports.push({ id: nid("spt"), slug, name, sortOrder: i }))
  for (let i = 0; i < N.competitions; i++) {
    const sport = db.sports[i % db.sports.length]
    db.competitions.push({ id: nid("cmp"), sportId: sport.id, name: `${sport.name} League ${i + 1}`, country: pick(CITIES) })
  }
  const partsBySport: Record<string, Participant[]> = {}
  for (const s of db.sports) {
    partsBySport[s.id] = []
    for (let j = 0; j < 12; j++) {
      const p: Participant = { id: nid("prt"), sportId: s.id, name: `${s.name.split(" ")[0]} ${pick(LAST)} ${j + 1}` }
      db.participants.push(p)
      partsBySport[s.id].push(p)
    }
  }

  // events + markets + selections
  for (let i = 0; i < N.events; i++) {
    const comp = db.competitions[i % db.competitions.length]
    const parts = partsBySport[comp.sportId]
    const home = parts[i % 12]
    const away = parts[(i + 3) % 12]
    const status: Event["status"] = i % 6 === 0 ? "LIVE" : i % 11 === 0 ? "FINISHED" : "SCHEDULED"
    const ev: Event = {
      id: nid("evt"),
      competitionId: comp.id,
      homeId: home.id,
      awayId: away.id,
      startsAt: new Date(now + ((i % 48) - 8) * 36e5).toISOString(),
      status,
      homeScore: status !== "SCHEDULED" ? i % 3 : 0,
      awayScore: status !== "SCHEDULED" ? (i >> 1) % 3 : 0,
      clockSeconds: status === "LIVE" ? 300 + ((i * 37) % 2400) : 0,
      simSeed: 1000 + i,
    }
    db.events.push(ev)
    for (const [mname, outcomes] of MARKET_DEFS) {
      const m: Market = { id: nid("mkt"), eventId: ev.id, name: mname, status: "OPEN" }
      db.markets.push(m)
      const base = 1.7 + (ev.simSeed % 40) / 100
      outcomes.forEach((oname, idx) => {
        db.selections.push({ id: nid("sel"), marketId: m.id, name: oname, odds: round2(base + 0.28 * idx) })
      })
    }
  }

  // seed bets + transactions + ledger
  for (let i = 0; i < N.bets; i++) {
    const user = customers[i % customers.length]
    const sel = db.selections[(i * 7) % db.selections.length]
    const market = db.markets.find((m) => m.id === sel.marketId)!
    const ev = db.events.find((e) => e.id === market.eventId)!
    const stake = 10 + (i % 20)
    const settled = i % 5 === 0
    const won = settled && i % 10 === 0
    const bet: Bet = {
      id: nid("bet"),
      ticketCode: `NX${String(i).padStart(5, "0")}`,
      userId: user.id,
      betType: "SINGLE",
      status: settled ? (won ? "WON" : "LOST") : "SUBMITTED",
      stake,
      combinedOdds: sel.odds,
      potentialPayout: round2(stake * sel.odds),
      selections: [
        {
          selectionId: sel.id,
          eventId: ev.id,
          marketName: market.name,
          selectionName: sel.name,
          eventLabel: eventLabel(db, ev),
          oddsAtPlacement: sel.odds,
        },
      ],
      createdAt: new Date(now - (i % 30) * 36e5).toISOString(),
      settledAt: settled ? new Date(now - (i % 20) * 36e5).toISOString() : null,
    }
    db.bets.push(bet)
    pushTx(db, user.id, "MOCK_BET", stake, bet.ticketCode, "seed mock bet")
  }

  // casino
  const providers = ["NovaSpin Demo", "TableLab Mock", "ArcadeSeed"]
  for (let i = 0; i < N.casino; i++) {
    db.casino.push({
      id: nid("csn"),
      providerId: providers[i % 3],
      name: `Demo ${pick(["Fortune", "Riches", "Gold", "Diamond", "Fruit", "Dragon", "Vegas"])} ${i + 1}`,
      category: CASINO_CATS[i % CASINO_CATS.length],
      mockRtp: 95 + round2(rnd() * 2),
      isNew: i < 8,
      isPopular: i % 4 === 0,
      isFeatured: i % 9 === 0,
    })
  }

  // promotions + banners + cms
  for (let i = 0; i < N.promotions; i++) {
    const published = i < N.promotions - 2
    db.promotions.push({
      id: nid("pro"),
      title: `Demo Boost ${i + 1}`,
      body: "Fictional promotional credit offer. DEMO CREDITS only.",
      theme: i % 2 === 0 ? "sports" : "casino",
      status: published ? "PUBLISHED" : "DRAFT",
      publishedAt: published ? new Date(now - i * 864e5).toISOString() : null,
      createdAt: new Date(now - (i + 5) * 864e5).toISOString(),
    })
  }
  db.banners.push(
    { id: nid("bnr"), title: "Golden Market Weekend Boost", subtitle: "DEMO CREDITS only", theme: "sports", sortOrder: 0 },
    { id: nid("bnr"), title: "New Demo Slots", subtitle: "Simulated outcomes", theme: "casino", sortOrder: 1 },
    { id: nid("bnr"), title: "Live Markets Lab", subtitle: "Accelerated mock clocks", theme: "live", sortOrder: 2 },
  )
  db.cms.push(
    { id: nid("cms"), contentType: "news_article", title: "PulSync demo season preview", body: "All figures are simulated in this mock environment.", status: "PUBLISHED", publishedAt: new Date(now).toISOString() },
    { id: nid("cms"), contentType: "faq", title: "Is this real money?", body: "No. This is a mock environment using DEMO CREDITS only.", status: "PUBLISHED", publishedAt: new Date(now).toISOString() },
    { id: nid("cms"), contentType: "announcement", title: "Welcome to the demo", body: "No real betting or payments occur here.", status: "DRAFT", publishedAt: null },
  )

  // tickets
  const support = demoUsers["support@example.test"]
  for (let i = 0; i < N.tickets; i++) {
    const cust = customers[i % customers.length]
    const t: SupportTicket = {
      id: nid("tkt"),
      customerId: cust.id,
      customerName: cust.displayName,
      assigneeId: i % 2 === 0 ? support.id : null,
      subject: `${pick(["Withdrawal", "Bonus", "Login", "Bet settlement", "Account"])} question ${i + 1}`,
      category: pick(["account", "payments", "betting", "bonus"]),
      status: i % 2 === 0 ? "ASSIGNED" : "OPEN",
      createdAt: new Date(now - i * 36e5).toISOString(),
      updatedAt: new Date(now - i * 36e5).toISOString(),
    }
    db.tickets.push(t)
    db.messages.push({
      id: nid("msg"),
      ticketId: t.id,
      authorId: cust.id,
      authorName: cust.displayName,
      body: "Hello, this is a synthetic support request for the demo environment.",
      internal: false,
      createdAt: t.createdAt,
    })
  }

  // risk alerts
  for (let i = 0; i < 8; i++) {
    const cust = customers[i]
    db.risk.push({
      id: nid("rsk"),
      userId: cust.id,
      userName: cust.displayName,
      alertType: i % 2 === 0 ? "velocity" : "unusual_activity",
      severity: i < 2 ? "HIGH" : i < 5 ? "MEDIUM" : "LOW",
      status: "OPEN",
      details: "Synthetic velocity pattern flagged for demo review.",
      createdAt: new Date(now - i * 72e5).toISOString(),
    })
  }

  // notifications
  for (let i = 0; i < N.notifications; i++) {
    const cust = customers[i % customers.length]
    db.notifications.push({
      id: nid("ntf"),
      userId: cust.id,
      title: pick(["Bet update", "Promo unlocked", "Welcome", "Security notice"]),
      body: "Simulated in-app notification. No email or SMS was sent.",
      read: i % 3 === 0,
      createdAt: new Date(now - i * 18e5).toISOString(),
    })
  }

  // flags + settings + audit
  db.flags.push(
    { key: "live_simulation", enabled: true, description: "Tick live clocks and odds" },
    { key: "casino_sim", enabled: true, description: "Local casino outcomes" },
    { key: "arena", enabled: true, description: "Social mock tickets" },
  )
  db.settings.push({ key: "demo_banner", value: "DEMO / MOCK ENVIRONMENT — DEMO CREDITS only" })
  db.audit.push({
    id: nid("aud"),
    actorId: demoUsers["admin@example.test"].id,
    actorRole: "ADMIN",
    action: "seed",
    resourceType: "system",
    resourceId: "",
    reason: "initial deterministic seed",
    createdAt: new Date(now).toISOString(),
  })
  for (let i = 0; i < N.audit; i++) {
    db.audit.push({
      id: nid("aud"),
      actorId: demoUsers["admin@example.test"].id,
      actorRole: "ADMIN",
      action: pick(["login", "odds.update", "promotions.publish", "support.respond"]),
      resourceType: pick(["event", "promotion", "ticket", "user"]),
      resourceId: String(i),
      reason: "seed activity",
      createdAt: new Date(now - i * 36e5).toISOString(),
    })
  }

  return db
}

export function eventLabel(db: Db, ev: Event): string {
  const home = db.participants.find((p) => p.id === ev.homeId)?.name ?? "Home"
  const away = db.participants.find((p) => p.id === ev.awayId)?.name ?? "Away"
  return `${home} v ${away}`
}

export function pushTx(db: Db, userId: string, type: Transaction["type"], amount: number, reference: string, note: string) {
  const tx: Transaction = { id: nid("tx"), userId, type, amount, reference, note, createdAt: new Date().toISOString() }
  db.transactions.push(tx)
  // double-entry-ish ledger
  if (type === "MOCK_BET") {
    db.ledger.push({ id: nid("led"), transactionId: tx.id, userId, account: "CUSTOMER_WALLET", debit: amount, credit: 0, createdAt: tx.createdAt })
    db.ledger.push({ id: nid("led"), transactionId: tx.id, userId, account: "PENDING_BETS", debit: 0, credit: amount, createdAt: tx.createdAt })
  } else if (type === "MOCK_PAYOUT" || type === "MOCK_REFUND") {
    db.ledger.push({ id: nid("led"), transactionId: tx.id, userId, account: "PENDING_BETS", debit: amount, credit: 0, createdAt: tx.createdAt })
    db.ledger.push({ id: nid("led"), transactionId: tx.id, userId, account: "CUSTOMER_WALLET", debit: 0, credit: amount, createdAt: tx.createdAt })
  } else {
    db.ledger.push({ id: nid("led"), transactionId: tx.id, userId, account: "HOUSE", debit: amount < 0 ? -amount : 0, credit: amount > 0 ? amount : 0, createdAt: tx.createdAt })
    db.ledger.push({ id: nid("led"), transactionId: tx.id, userId, account: "CUSTOMER_WALLET", debit: amount > 0 ? amount : 0, credit: amount < 0 ? -amount : 0, createdAt: tx.createdAt })
  }
  return tx
}

export function nextId(prefix: string) {
  return nid(prefix)
}

// ---- singleton across HMR ----
const g = globalThis as unknown as { __PSK_DB__?: Db }
export function getDb(): Db {
  if (!g.__PSK_DB__) g.__PSK_DB__ = buildDb()
  return g.__PSK_DB__
}
export function resetDb(): Db {
  const prev = g.__PSK_DB__
  const fresh = buildDb()
  // preserve active sessions (user ids are deterministic across rebuilds)
  if (prev) {
    for (const [token, userId] of prev.sessions) {
      if (fresh.users.some((u) => u.id === userId)) fresh.sessions.set(token, userId)
    }
  }
  g.__PSK_DB__ = fresh
  return fresh
}
