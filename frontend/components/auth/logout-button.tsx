"use client";

import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";

export function LogoutButton() {
  const router = useRouter();

  async function handleLogout() {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
    } catch (error) {
      console.error("[LogoutButton.handleLogout] logout request failed", error);
    }
    router.push("/login");
    router.refresh();
  }

  return (
    <Button variant="ghost" onClick={handleLogout}>
      Log out
    </Button>
  );
}
