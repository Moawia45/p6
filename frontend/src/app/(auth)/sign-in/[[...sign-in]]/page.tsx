/**
 * ConstructMind AI - Clerk SignIn Page
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

import { SignIn } from '@/lib/clerk-compat';

export default function SignInPage() {
  return (
    <SignIn
      path="/sign-in"
      routing="path"
      signUpUrl="/sign-up"
      fallbackRedirectUrl="/dashboard"
    />
  );
}
