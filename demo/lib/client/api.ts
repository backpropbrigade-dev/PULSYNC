type ApiError = { error?: string; detail?: string }

const externalApiUrl =
  process.env.NEXT_PUBLIC_API_URL?.trim() ||
  process.env.VITE_API_URL?.trim() ||
  ""

export function isExternalApiConfigured(): boolean {
  return true
}

function resolveUrl(url: string): string {
  if (!externalApiUrl || url.startsWith("http")) return url
  return `${externalApiUrl.replace(/\/$/, "")}${url.startsWith("/") ? url : `/${url}`}`
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(resolveUrl(url), {
    ...init,
    credentials: externalApiUrl ? "include" : "same-origin",
    headers: { Accept: "application/json", ...init?.headers },
  })
  const data = (await res.json().catch(() => ({}))) as T & ApiError
  if (!res.ok) throw new Error(data.error || data.detail || `Request failed (${res.status})`)
  return data
}

export async function apiGet<T = unknown>(url: string): Promise<T> {
  return request<T>(url)
}

export async function apiPost<T = unknown>(url: string, body?: unknown): Promise<T> {
  return request<T>(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  })
}

export const fetcher = (url: string) => apiGet(url)

export function fmtCredits(n: number | undefined | null): string {
  if (n === undefined || n === null || Number.isNaN(n)) return "0.00"
  return new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n)
}
