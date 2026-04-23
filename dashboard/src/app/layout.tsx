import type { Metadata } from 'next';

import { inter, jetbrainsMono } from './fonts';
import './globals.css';

export const metadata: Metadata = {
  title: 'PANOPTICON LIVE',
  description:
    'Proprietary biometric fatigue telemetry extracted from 2D tennis broadcast pixels.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="min-h-full">{children}</body>
    </html>
  );
}
