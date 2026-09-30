import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { exchangeGoogleCode } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { SESSION_COOKIE, SESSION_MAX_AGE_SECONDS } from "@/lib/auth/constants";

export async function GET(request: NextRequest): Promise<NextResponse> {
  const code = request.nextUrl.searchParams.get("code");
  if (!code) {
    return NextResponse.redirect(new URL("/login?error=google_oauth_failed", request.url));
  }

  try {
    const { access_token } = await exchangeGoogleCode(code);
    const cookieStore = await cookies();
    cookieStore.set(SESSION_COOKIE, access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: SESSION_MAX_AGE_SECONDS,
    });
    return NextResponse.redirect(new URL("/dashboard", request.url));
  } catch (error) {
    if (error instanceof ApiError) {
      console.error("[auth.callback] exchange rejected", error.status);
    } else {
      console.error("[auth.callback] exchange failed", error);
    }
    return NextResponse.redirect(new URL("/login?error=google_oauth_failed", request.url));
  }
}
