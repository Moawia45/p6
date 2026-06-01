/**
 * ConstructMind AI - Root Layout
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import { ClerkProvider } from '@/lib/clerk-compat';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
  preload: false,
});

export const metadata: Metadata = {
  title: 'ConstructMind AI | AI-Powered Construction Intelligence',
  description: 'Primavera P6 replacement with AI scheduling, BOQ parsing, and forensic delay analysis.',
  authors: [{ name: 'Moawia Husnain | Civil Engineer' }],
  keywords: ['Primavera P6', 'Construction Management', 'AI Copilot', 'BOQ Analysis', 'CPM Scheduling'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider
      appearance={{
        variables: {
          colorPrimary: '#3b82f6',
          colorBackground: '#0c0c1d',
          colorText: '#e4e4f0',
          colorTextSecondary: '#8888aa',
        },
      }}
    >
      <html lang="en" className="dark scroll-smooth">
        <body
          className={`${inter.variable} ${jetbrainsMono.variable} font-sans bg-background text-foreground antialiased min-h-screen overflow-x-hidden`}
        >
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
