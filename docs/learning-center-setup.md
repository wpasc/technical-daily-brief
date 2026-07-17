# Learning Center — one-time account setup

The app code deploys itself; these are the account-side steps only the owner
can do. Order matters only in that Vercel wants the env vars at the end.

## 1. Neon (database)

1. Create a project at [neon.tech](https://neon.tech) (free tier).
2. Copy the connection string (with `?sslmode=require`) — this is
   `DATABASE_URL`.

## 2. Google OAuth client (login)

1. [console.cloud.google.com](https://console.cloud.google.com) → APIs &
   Services → Credentials → Create credentials → OAuth client ID →
   Web application.
2. Authorized redirect URIs — add both:
   - `http://localhost:3000/api/auth/callback/google`
   - `https://<your-app>.vercel.app/api/auth/callback/google`
     (add this after Vercel assigns the domain in step 3)
3. Copy client ID → `AUTH_GOOGLE_ID`, client secret → `AUTH_GOOGLE_SECRET`.

## 3. Vercel (hosting)

1. [vercel.com](https://vercel.com) → Add New Project → import
   `wpasc/technical-daily-brief`. Framework auto-detects as Next.js; no
   build settings needed.
2. Project → Settings → Environment Variables: set `AUTH_SECRET`
   (`openssl rand -base64 32`), `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`,
   `AUTH_ALLOWED_EMAIL`, `DATABASE_URL`.
3. Account → Billing: confirm Hobby tier and set a spend cap.
4. Deploy. Visit the URL: you should be bounced to Google sign-in; your
   email gets in, any other account is rejected.

## Local dev

```bash
cp .env.example .env.local   # fill in the same values
npm install
npm run dev                  # http://localhost:3000
```

The Neon panel on the home page shows "not configured" until `DATABASE_URL`
is set — the auth gate works without it.
