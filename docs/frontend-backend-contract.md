# Frontend-backend contract

The current frontend is a Next.js application in `demo/`. When `VITE_API_URL`
or `NEXT_PUBLIC_API_URL` is configured, its centralized client uses that
FastAPI origin; without it, the existing local mock routes remain active.

## Compliance

- `POST /api/compliance/age-verification`
- Request: `{ "age": 24 }`
- `POST /api/compliance/self-exclusion-check`
- Request: `{ "anonymous_user_id": "..." }`

The shared `verifyAccess()` helper blocks the flow when either response is not
accepted. These are demo integrations only and must not be represented as
production EUDI Wallet or PSK verification.

## Session lifecycle

- `POST /api/sessions`
- Request: `{ "anonymous_user_id": "..." }`
- Response: `{ "session_id": "...", "user_id": "...", "started_at": "..." }`

The anonymous user ID is stored in `localStorage`; the active session is stored
in `sessionStorage`. No names, payment data, or other sensitive information is
stored.

## Events and intelligence

- `POST /api/sessions/{session_id}/events`
- Payload includes `event_type`, `page`, `action`, optional context fields,
  `session_id`, and an ISO `timestamp`.
- The optional response field `intelligence` may contain `intent`,
  `abandonment`, `friction`, `recommendations`, `guidance`, and
  `session_quality`.

The initial integration tracks `session_start` and meaningful `page_view`
navigation events. Additional match-specific actions can use the shared
`trackEvent()` helper.

## Recommendations and outcomes

- `GET /api/recommendations/{session_id}`
- `POST /api/recommendations/{session_id}/feedback`
- `POST /api/outcomes`

The backend remains the source of truth for recommendation ranking,
intelligence, and session quality. The frontend does not calculate these
values.

## Dashboard

The planned dashboard endpoints are:

- `GET /api/dashboard/metrics`
- `GET /api/dashboard/segments`
- `GET /api/dashboard/recommendations`
- `GET /api/dashboard/quality`
- `GET /api/dashboard/impact`

Historical reconstructed sessions must be labeled as proxies rather than live
frontend sessions.
