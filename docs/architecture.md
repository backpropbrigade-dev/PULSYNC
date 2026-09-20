# Architecture

## Current working prototype

The working frontend is a self-contained Next.js application in `demo/`.
Routes live under `demo/app/`, reusable UI under `demo/components/`, shared
types and services under `demo/lib/`, and static assets under `demo/public/`.
The `demo/app/api/` routes and server helpers provide mock behavior for local
demonstration.

The application can run directly with pnpm or as the `demo` service in the
root `docker-compose.yml`. The Docker image uses Next.js standalone output.

## Intended integrated architecture

The repository is organized to support independent workstreams:

- `demo/`: frontend prototype and demo assets
- `src/`: reserved for shared or integrated application source
- `tests/`: repository-level validation
- Backend: FastAPI/Python, to be integrated from its own workstream
- AI/ML: Python, to be integrated from its own workstream
- Database: Supabase/PostgreSQL

The backend and AI services are intentionally not claimed as implemented by the
current frontend branch.