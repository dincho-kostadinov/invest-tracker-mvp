import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { SESSION_COOKIE } from "@/lib/auth/constants";

// Optimistic check only: presence of the cookie, not signature/expiry
// verification (see specs/01-auth-app-shell.md). The backend independently
// validates the JWT on every API call, so this is a UX gate, not the
// security boundary.
const PUBLIC_ROUTES = new Set(["/", "/login", "/signup", "/auth/callback"]);
const AUTH_ENTRY_ROUTES = new Set(["/login", "/signup"]);

export function proxy(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;
  const isAuthenticated = request.cookies.has(SESSION_COOKIE);

  if (!PUBLIC_ROUTES.has(pathname) && !isAuthenticated) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (AUTH_ENTRY_ROUTES.has(pathname) && isAuthenticated) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|.*\\.(?:ico|png|jpg|jpeg|svg|webp|gif|css|js|map|txt|xml)$).*)",
  ],
};
