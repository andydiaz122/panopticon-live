import { Inter, JetBrains_Mono } from 'next/font/google';

/**
 * Inter Variable — primary UI face.
 * Preloaded (NOT font-display: swap) per anti-pattern #28 / Vercel deployment traps.
 */
export const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
  weight: ['400', '500', '600', '700'],
});

/**
 * JetBrains Mono — stat values and JSON display.
 * tabular-nums is applied at the CSS level where numbers render.
 */
export const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
  weight: ['400', '500', '600'],
});
