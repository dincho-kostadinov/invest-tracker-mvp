import { AuthForm } from "@/components/auth/auth-form";

const ERROR_MESSAGES: Record<string, string> = {
  google_oauth_failed: "Google sign-in didn't work. Please try again or use email/password.",
};

export default async function LoginPage(props: PageProps<"/login">) {
  const searchParams = await props.searchParams;
  const errorParam = searchParams.error;
  const errorCode = Array.isArray(errorParam) ? errorParam[0] : errorParam;
  const initialError = errorCode ? ERROR_MESSAGES[errorCode] : undefined;

  return (
    <AuthForm
      title="Sign in to Invest Tracker"
      subtitle="Track funds, gold and stocks in one place"
      submitLabel="Sign in"
      pendingLabel="Signing in..."
      footerText="Don't have an account?"
      footerLinkText="Create one"
      footerLinkHref="/signup"
      action="/api/auth/login"
      initialError={initialError}
    />
  );
}
