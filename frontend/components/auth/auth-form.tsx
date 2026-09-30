"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { z } from "zod";

import { LogoMark } from "@/components/brand/logo-mark";
import { GoogleIcon } from "@/components/icons/google-icon";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { API_BASE_URL } from "@/lib/api/client";

// Login only checks "is this filled in" — the backend is the source of truth
// on whether it's correct. Signup enforces the real password rules,
// including bcrypt's 72-*byte* (not character) limit — see
// backend/app/core/security.py.
const loginSchema = z.object({
  email: z.email({ error: "Enter a valid email" }),
  password: z.string().min(1, { error: "Enter your password" }),
});

const signupSchema = z.object({
  email: z.email({ error: "Enter a valid email" }),
  password: z
    .string()
    .min(8, { error: "Must be at least 8 characters" })
    .refine((value) => new TextEncoder().encode(value).length <= 72, {
      error: "Password is too long",
    }),
});

interface AuthFormProps {
  title: string;
  subtitle: string;
  submitLabel: string;
  pendingLabel: string;
  footerText: string;
  footerLinkText: string;
  footerLinkHref: string;
  action: "/api/auth/login" | "/api/auth/signup";
  initialError?: string;
}

export function AuthForm({
  title,
  subtitle,
  submitLabel,
  pendingLabel,
  footerText,
  footerLinkText,
  footerLinkHref,
  action,
  initialError,
}: AuthFormProps) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(initialError ?? null);
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const schema = action === "/api/auth/signup" ? signupSchema : loginSchema;
    const parsed = schema.safeParse({ email, password });
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? "Invalid input");
      return;
    }

    setPending(true);
    try {
      const response = await fetch(action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed.data),
      });
      if (!response.ok) {
        const data = (await response.json().catch(() => null)) as { error?: string } | null;
        setError(data?.error ?? "Something went wrong");
        return;
      }
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      console.error("[AuthForm.handleSubmit] request failed", err);
      setError("Something went wrong");
    } finally {
      setPending(false);
    }
  }

  return (
    <Card className="w-full max-w-[420px]">
      <CardHeader className="items-center text-center">
        <div className="mb-3 flex size-11 items-center justify-center rounded-lg bg-accent">
          <LogoMark className="size-6 text-primary-foreground" />
        </div>
        <CardTitle className="text-[22px]">{title}</CardTitle>
        <p className="text-[13.5px] text-muted-foreground">{subtitle}</p>
      </CardHeader>

      <CardContent className="flex flex-col gap-4">
        <Button asChild variant="outline" className="w-full">
          <a href={`${API_BASE_URL}/auth/google/login`}>
            <GoogleIcon className="size-4" />
            Continue with Google
          </a>
        </Button>

        <div className="flex items-center gap-3">
          <Separator className="flex-1" />
          <span className="text-[11.5px] font-semibold text-faint">OR</span>
          <Separator className="flex-1" />
        </div>

        <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>
          {error && <p className="text-[12.5px] font-medium text-loss">{error}</p>}
          <Button type="submit" disabled={pending} className="w-full">
            {pending ? pendingLabel : submitLabel}
          </Button>
        </form>

        <p className="text-center text-[12.5px] text-muted-foreground">
          {footerText}{" "}
          <Link href={footerLinkHref} className="font-medium text-accent hover:underline">
            {footerLinkText}
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
