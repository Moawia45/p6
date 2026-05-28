/**
 * ConstructMind AI - Clerk SignUp Page
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <SignUp
      path="/sign-up"
      routing="path"
      signInUrl="/sign-in"
      fallbackRedirectUrl="/dashboard"
    />
  );
}
