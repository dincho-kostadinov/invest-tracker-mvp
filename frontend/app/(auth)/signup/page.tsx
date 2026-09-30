import { AuthForm } from "@/components/auth/auth-form";

export default function SignupPage() {
  return (
    <AuthForm
      title="Create your account"
      subtitle="Track funds, gold and stocks in one place"
      submitLabel="Sign up"
      pendingLabel="Creating account..."
      footerText="Already have an account?"
      footerLinkText="Sign in"
      footerLinkHref="/login"
      action="/api/auth/signup"
    />
  );
}
