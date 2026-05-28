'use client';

import * as React from 'react';
import * as Clerk from '@clerk/nextjs';

const hasClerkKeys = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && 
                     process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY !== "pk_test_dGVzdC1jbGVyay1rZXktOTkuY2xlcmsuYWNjb3VudHMuZGV2JA==";

export function ClerkProvider({ children, ...props }: any) {
  if (hasClerkKeys) {
    return <Clerk.ClerkProvider {...props}>{children}</Clerk.ClerkProvider>;
  }
  return <>{children}</>;
}

export function useUser() {
  if (hasClerkKeys) {
    try {
      return Clerk.useUser();
    } catch (e) {
      console.warn("Clerk context useUser error:", e);
    }
  }
  return {
    isSignedIn: true, // Auto-signed in for mock/preview mode
    user: {
      fullName: 'Moawia Husnain',
      imageUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=256&auto=format&fit=crop',
      primaryEmailAddress: { emailAddress: 'moawia@example.com' }
    },
    isLoaded: true
  };
}

export function UserButton({ appearance }: any) {
  if (hasClerkKeys) {
    return <Clerk.UserButton appearance={appearance} />;
  }
  return (
    <div className="h-8 w-8 rounded-xl border border-white/10 overflow-hidden bg-zinc-800 flex items-center justify-center text-xs font-bold text-white cursor-pointer hover:bg-zinc-700 transition-colors">
      MH
    </div>
  );
}

export function SignInButton({ children, mode }: any) {
  if (hasClerkKeys) {
    return <Clerk.SignInButton mode={mode}>{children}</Clerk.SignInButton>;
  }
  return <>{children}</>;
}

export function SignIn() {
  if (hasClerkKeys) {
    return <Clerk.SignIn />;
  }
  return (
    <div className="text-white text-center p-8 bg-zinc-900/50 border border-white/5 rounded-2xl">
      <h2 className="text-lg font-bold mb-2">Clerk Sign In Mode</h2>
      <p className="text-sm text-zinc-400">Configure your Clerk keys in your environment variables to enable user login.</p>
    </div>
  );
}

export function SignUp() {
  if (hasClerkKeys) {
    return <Clerk.SignUp />;
  }
  return (
    <div className="text-white text-center p-8 bg-zinc-900/50 border border-white/5 rounded-2xl">
      <h2 className="text-lg font-bold mb-2">Clerk Sign Up Mode</h2>
      <p className="text-sm text-zinc-400">Configure your Clerk keys in your environment variables to enable user registration.</p>
    </div>
  );
}
