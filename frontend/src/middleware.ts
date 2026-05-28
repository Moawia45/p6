/**
 * ConstructMind AI - Middleware
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 * 
 * Pass-through middleware (temporarily bypassing Clerk authentication
 * to prevent 500 errors on Vercel when keys are not configured yet).
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export default function middleware(request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};
