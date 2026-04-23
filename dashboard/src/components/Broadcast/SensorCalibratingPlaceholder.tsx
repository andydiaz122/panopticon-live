'use client';

import { motion } from 'framer-motion';

import { colors, motion as motionTokens } from '@/lib/design-tokens';

/**
 * Rendered on the right rail while `activeHUDLayout === null` (before the
 * backend's warmup filter releases the first layout).
 *
 * Per GOTCHA-017: the warmup window would otherwise leave the right rail
 * blank for ~11 seconds — judges would assume the app is broken. This
 * placeholder turns the constraint into broadcast-grade "telemetry is
 * warming up" framing.
 *
 * Data-driven gate (PATTERN-048): SignalRail decides when to mount/unmount
 * this component based on `currentTimeMs < firstLayoutMs`. This component
 * just renders the visual; it does not read time itself.
 */
export default function SensorCalibratingPlaceholder() {
  return (
    <motion.section
      role="status"
      aria-live="polite"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={motionTokens.springStandard}
      className="flex h-full w-full flex-col gap-4 rounded-lg border p-5"
      style={{
        background: colors.bg1,
        borderColor: colors.border,
        minHeight: 320,
      }}
    >
      <div
        className="mono text-[11px] uppercase tracking-[0.18em]"
        style={{ color: colors.textSecondary }}
      >
        Biometric Sensors
      </div>

      <motion.div
        className="mono text-[20px] font-semibold tracking-[0.08em]"
        style={{ color: colors.playerA }}
        animate={{ opacity: [0.55, 1, 0.55] }}
        transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
      >
        CALIBRATING…
      </motion.div>

      <motion.div
        className="flex items-center gap-2"
        variants={dotContainerVariants}
        initial="initial"
        animate="animate"
      >
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            variants={dotVariants}
            className="inline-block h-2 w-2 rounded-full"
            style={{ background: colors.playerA }}
          />
        ))}
      </motion.div>

      <p
        className="mt-auto text-[12px] leading-relaxed"
        style={{ color: colors.textSecondary }}
      >
        Establishing player baselines from warmup. The first wave of fatigue
        telemetry will appear when Player A&rsquo;s baseline locks in.
      </p>
    </motion.section>
  );
}

import type { Variants } from 'framer-motion';

const dotContainerVariants: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.18,
    },
  },
};

const dotVariants: Variants = {
  initial: { opacity: 0.3, scale: 0.8 },
  animate: {
    opacity: [0.3, 1, 0.3],
    scale: [0.8, 1.05, 0.8],
    transition: {
      duration: 1.2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};
