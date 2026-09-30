"use client";

import { useEffect } from "react";

import { Button } from "@/components/ui/button";

export default function AppError({
  error,
  retry,
}: {
  error: Error & { digest?: string };
  retry: () => void;
}) {
  useEffect(() => {
    console.error("[AppError] unhandled error in (app)", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background p-6 text-center">
      <h1 className="text-[22px] font-bold text-foreground">Something went wrong</h1>
      <p className="max-w-sm text-[13.5px] font-medium text-muted-foreground">
        We couldn&apos;t load this page. This is usually temporary.
      </p>
      <Button onClick={() => retry()}>Try again</Button>
    </div>
  );
}
