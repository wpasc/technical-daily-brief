# Next.js on Vercel with Neon Postgres

The v0 architecture deliberately deferred client-side JS and any backend
until real interactivity and an authenticated personal layer existed; both
triggers have now fired at once — the site becomes a single-user, fully
auth-gated learning app. Chose Next.js deployed on Vercel with Neon Postgres
over container PaaS (Fly.io/Railway), Cloudflare Workers + D1, and a bare
VPS: effectively zero cost at single-user scale with spend caps, zero ops,
and learning this stack is itself a project goal. The static
GitHub Pages site is retired once the app serves the briefs.
