import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { z } from "zod";

import { signup } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { SESSION_COOKIE, SESSION_MAX_AGE_SECONDS } from "@/lib/auth/constants";

// This Route Handler is a public HTTP endpoint like any other — it must
// validate independently of the React form, not rely on client-side checks.
// bcrypt's limit is 72 *bytes*, not characters (see
// backend/app/core/security.py), so the byte check is required, not just the
// character-count one.
const bodySchema = z.object({
  email: z.email(),
  password: z
    .string()
    .min(8)
    .refine((value) => new TextEncoder().encode(value).length <= 72),
});

export async function POST(request: Request): Promise<NextResponse> {
  const parsed = bodySchema.safeParse(await request.json());
  if (!parsed.success) {
    return NextResponse.json(
      { error: "Enter a valid email and a password of at least 8 characters" },
      { status: 400 }
    );
  }

  try {
    const { access_token } = await signup(parsed.data.email, parsed.data.password);
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
    if (error instanceof ApiError && error.status === 409) {
      return NextResponse.json({ error: "Email is already registered" }, { status: 409 });
    }
    if (error instanceof ApiError && error.status === 422) {
      return NextResponse.json({ error: "Enter a valid email and password" }, { status: 400 });
    }
    console.error("[api.auth.signup] signup failed", error);
    return NextResponse.json({ error: "Something went wrong" }, { status: 500 });
  }
}
