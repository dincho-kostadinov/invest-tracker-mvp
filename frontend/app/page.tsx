import { redirect } from "next/navigation";

import { getSessionToken } from "@/lib/auth/session";

export default async function RootPage(): Promise<never> {
  const token = await getSessionToken();
  redirect(token ? "/dashboard" : "/login");
}
