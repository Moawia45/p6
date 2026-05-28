/**
 * ConstructMind AI - Middleware
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 * 
 * Clerk authentication middleware for route protection.
 */

import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhook(.*)',
]);

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

let middlewareHandler;

if (process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && process.env.CLERK_SECRET_KEY) {
  middlewareHandler = clerkMiddleware(async (auth, request) => {
    if (!isPublicRoute(request)) {
      await auth.protect();
    }
  });
} else {
  // No-op fallback when Clerk keys are not configured yet on Vercel/Local
  middlewareHandler = () => {
    return NextResponse.next();
  };
}

export default middlewareHandler;

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};
