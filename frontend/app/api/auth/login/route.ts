import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { z } from "zod";

import { login } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { SESSION_COOKIE, SESSION_MAX_AGE_SECONDS } from "@/lib/auth/constants";

const bodySchema = z.object({
  email: z.email(),
  password: z.string().min(1),
});

export async function POST(request: Request): Promise<NextResponse> {
  const parsed = bodySchema.safeParse(await request.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid email or password" }, { status: 400 });
  }

  try {
    const { access_token } = await login(parsed.data.email, parsed.data.password);
    const cookieStore = await cookies();
    cookieStore.set(SESSION_COOKIE, access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: SESSION_MAX_AGE_SECONDS,
    });
    return NextResponse.json({ ok: true });
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return NextResponse.json({ error: "Invalid email or password" }, { status: 401 });
    }
    console.error("[api.auth.login] login failed", error);
    return NextResponse.json({ error: "Something went wrong" }, { status: 500 });
  }
}
