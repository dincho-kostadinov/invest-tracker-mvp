import { getHealth } from "@/lib/api/health";

export default async function Home() {
  let status = "unreachable";
  let database = "unknown";

  try {
    const health = await getHealth();
    status = health.status;
    database = health.database;
  } catch (error) {
    console.error("[page.Home] health check failed", error);
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-zinc-50 font-sans dark:bg-black">
      <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">Invest Tracker</h1>
      <p className="text-zinc-600 dark:text-zinc-400">
        Backend status: <span className="font-mono">{status}</span> · Database:{" "}
        <span className="font-mono">{database}</span>
      </p>
    </div>
  );
}
