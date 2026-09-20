# Dependencies

## Frontend demo

The authoritative dependency manifest and lockfile are:

- [`demo/package.json`](../demo/package.json)
- [`demo/pnpm-lock.yaml`](../demo/pnpm-lock.yaml)

Install reproducibly with:

```powershell
cd demo
pnpm install --frozen-lockfile
```

The demo uses Next.js, React, TypeScript, Tailwind CSS, Recharts, SWR, Zustand,
and the UI utilities listed in its manifest.

## Other workstreams

The root `requirements.txt` is currently empty on this branch. Backend and AI
Python dependencies should be added by their owning workstreams when those
implementations are integrated.