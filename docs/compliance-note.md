# Compliance note

This branch contains a local demonstration frontend with mock data and mock API
routes. It does not contain production credentials, customer data, payment
information, or connections to Supabase/PostgreSQL.

Do not commit API keys, passwords, tokens, database secrets, personal data, or
real player data. Local environment files are ignored by the repository
configuration; use `.env.example` for non-secret variable documentation.

Production security, authentication, data retention, and regulatory controls
remain to be defined with the backend, AI, and database workstreams before
deployment.