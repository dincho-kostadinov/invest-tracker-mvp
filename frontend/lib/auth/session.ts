import { cookies } from "next/headers";

import { SESSION_COOKIE } from "@/lib/auth/constants";

export async function getSessionToken(): Promise<string | undefined> {
  const store = await cookies();
  return store.get(SESSION_COOKIE)?.value;
}

export async function getAuthHeader(): Promise<string | undefined> {
  const token = await getSessionToken();
  return token ? `Bearer ${token}` : undefined;
}
