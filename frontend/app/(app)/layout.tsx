import Link from "next/link";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";

import { getMe } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";
import { getAuthHeader } from "@/lib/auth/session";
import { LogoMark } from "@/components/brand/logo-mark";
import { LogoutButton } from "@/components/auth/logout-button";
import { NavLink } from "@/components/nav/nav-link";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/holdings", label: "Holdings" },
  { href: "/transactions", label: "Transactions" },
  { href: "/settings", label: "Settings" },
];

export default async function AppLayout({ children }: { children: ReactNode }) {
  const authHeader = await getAuthHeader();
  if (!authHeader) {
    redirect("/login");
  }

  let user;
  try {
    user = await getMe(authHeader);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      redirect("/login");
    }
    throw error;
  }

  const initials = (user.name ?? user.email).charAt(0).toUpperCase();

  return (
    <div className="min-h-screen bg-background">
      <header className="flex h-[60px] items-center justify-between border-b border-border bg-card px-6">
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="flex size-7 items-center justify-center rounded-md bg-accent">
              <LogoMark className="size-4 text-primary-foreground" />
            </div>
            <span className="text-[14.5px] font-semibold text-foreground">Invest Tracker</span>
          </Link>
          <nav className="flex items-center gap-1">
            {NAV_LINKS.map((link) => (
              <NavLink key={link.href} href={link.href}>
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <span className="rounded-full border border-border px-2.5 py-0.5 text-[11.5px] font-semibold text-muted-foreground">
            EUR
          </span>
          <Avatar>
            <AvatarFallback>{initials}</AvatarFallback>
          </Avatar>
          <LogoutButton />
        </div>
      </header>
      <main className="mx-auto max-w-[1280px] p-6">{children}</main>
    </div>
  );
}
