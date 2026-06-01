'use client';

import * as React from 'react';

const hasClerkKeys = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && 
                     process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY !== '' &&
                     process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY !== 'pk_test_dGVzdC1jbGVyay1rZXktOTkuY2xlcmsuYWNjb3VudHMuZGV2JA==';

// Dynamically loaded Clerk module (only when keys exist)
let ClerkModule: any = null;
if (hasClerkKeys) {
  // Dynamic import at module scope for client components
  import('@clerk/nextjs').then(mod => { ClerkModule = mod; }).catch(() => {});
}

export function ClerkProvider({ children, ...props }: any) {
  const [Mod, setMod] = React.useState<any>(ClerkModule);
  
  React.useEffect(() => {
    if (hasClerkKeys && !Mod) {
      import('@clerk/nextjs').then(m => { setMod(m); ClerkModule = m; }).catch(() => {});
    }
  }, [Mod]);
  
  if (hasClerkKeys && Mod?.ClerkProvider) {
    return <Mod.ClerkProvider {...props}>{children}</Mod.ClerkProvider>;
  }
  return <>{children}</>;
}

export function useUser() {
  if (hasClerkKeys && ClerkModule?.useUser) {
    try {
      return ClerkModule.useUser();
    } catch (e) {
      console.warn('Clerk useUser error:', e);
    }
  }
  return {
    isSignedIn: true,
    user: {
      fullName: 'Moawia Husnain',
      imageUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=256&auto=format&fit=crop',
      primaryEmailAddress: { emailAddress: 'moawia@example.com' }
    },
    isLoaded: true
  };
}

export function UserButton({ appearance }: any) {
  if (hasClerkKeys && ClerkModule?.UserButton) {
    return <ClerkModule.UserButton appearance={appearance} />;
  }
  return (
    <div className="h-8 w-8 rounded-xl border border-white/10 overflow-hidden bg-zinc-800 flex items-center justify-center text-xs font-bold text-white cursor-pointer hover:bg-zinc-700 transition-colors">
      MH
    </div>
  );
}

export function SignInButton({ children, mode }: any) {
  if (hasClerkKeys && ClerkModule?.SignInButton) {
    return <ClerkModule.SignInButton mode={mode}>{children}</ClerkModule.SignInButton>;
  }
  return <>{children}</>;
}

export function SignIn(props: any) {
  if (hasClerkKeys && ClerkModule?.SignIn) {
    return <ClerkModule.SignIn {...props} />;
  }
  return (
    <div className="text-white text-center p-8 bg-zinc-900/50 border border-white/5 rounded-2xl">
      <h2 className="text-lg font-bold mb-2">Clerk Sign In Mode</h2>
      <p className="text-sm text-zinc-400">Configure your Clerk keys in your environment variables to enable user login.</p>
    </div>
  );
}

export function SignUp(props: any) {
  if (hasClerkKeys && ClerkModule?.SignUp) {
    return <ClerkModule.SignUp {...props} />;
  }
  return (
    <div className="text-white text-center p-8 bg-zinc-900/50 border border-white/5 rounded-2xl">
      <h2 className="text-lg font-bold mb-2">Clerk Sign Up Mode</h2>
      <p className="text-sm text-zinc-400">Configure your Clerk keys in your environment variables to enable user registration.</p>
    </div>
  );
}
