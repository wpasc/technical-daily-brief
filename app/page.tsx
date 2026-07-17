import { auth, signOut } from "@/auth";
import { neon } from "@neondatabase/serverless";

async function dbNow(): Promise<string> {
  if (!process.env.DATABASE_URL) return "not configured";
  try {
    const sql = neon(process.env.DATABASE_URL);
    const rows = await sql`select now()`;
    return `connected — server time ${rows[0].now}`;
  } catch (e) {
    return `error — ${e instanceof Error ? e.message : String(e)}`;
  }
}

export default async function Home() {
  const session = await auth();
  const db = await dbNow();

  return (
    <main>
      <h1>Learning Center</h1>
      <p className="muted">
        Signed in as {session?.user?.email ?? "unknown"}. Neon: {db}.
      </p>
      <p>
        Nothing here yet — the sync engine, review queue, and reading views
        arrive next (WPA-290..292).
      </p>
      <form
        action={async () => {
          "use server";
          await signOut();
        }}
      >
        <button type="submit">Sign out</button>
      </form>
    </main>
  );
}
