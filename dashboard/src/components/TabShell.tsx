'use client';

import { motion } from 'framer-motion';
import {
  useState,
  type ReactNode,
} from 'react';

import { colors, motion as motionTokens } from '@/lib/design-tokens';

/**
 * Top-level 2K-Sports tab navigation shell.
 *
 * Keep-alive semantics (PATTERN-050): all tab bodies stay MOUNTED across tab
 * switches via `display: none` on inactive panels. This preserves:
 *   - Video playback state (continuous playback while user browses tabs)
 *   - Scroll positions (SignalFeed's auto-scrolled log stays where it was)
 *   - React state inside each tab body
 *
 * The alternative (unmount on switch) would pause the video AND reset the
 * PanopticonProvider's rAF loop every time the user switches tabs. That breaks
 * the demo pacing (auto-pause timeline, typewriter state).
 */

export interface TabDef {
  id: string;
  label: string;
  sublabel?: string;
  /** Rendered inside the panel container. Stays mounted across tab switches. */
  content: ReactNode;
}

export interface TabShellProps {
  tabs: ReadonlyArray<TabDef>;
  initialTabId?: string;
}

export default function TabShell({ tabs, initialTabId }: TabShellProps) {
  const [activeId, setActiveId] = useState<string>(
    initialTabId ?? tabs[0]?.id ?? '',
  );

  return (
    <div className="flex min-h-screen w-full flex-col">
      <TabNav tabs={tabs} activeId={activeId} onSelect={setActiveId} />

      <div className="relative flex-1">
        {tabs.map((tab) => (
          <div
            key={tab.id}
            role="tabpanel"
            aria-labelledby={`tab-${tab.id}`}
            aria-hidden={tab.id !== activeId}
            style={{ display: tab.id === activeId ? 'block' : 'none' }}
          >
            {tab.content}
          </div>
        ))}
      </div>
    </div>
  );
}

interface TabNavProps {
  tabs: ReadonlyArray<TabDef>;
  activeId: string;
  onSelect: (id: string) => void;
}

function TabNav({ tabs, activeId, onSelect }: TabNavProps) {
  return (
    <nav
      role="tablist"
      aria-label="Panopticon views"
      className="sticky top-0 z-20 flex items-center gap-1 border-b px-6 py-3 backdrop-blur"
      style={{
        background: `${colors.bg0}E6`,
        borderColor: colors.border,
      }}
    >
      {/* Brand mark */}
      <div className="mr-4 flex items-center gap-2">
        <span
          className="inline-block h-2 w-2 rounded-full"
          style={{ background: colors.playerA, boxShadow: `0 0 10px ${colors.playerA}` }}
        />
        <span
          className="mono text-[11px] font-bold uppercase tracking-[0.22em]"
          style={{ color: colors.textPrimary }}
        >
          Panopticon Live
        </span>
      </div>

      {tabs.map((tab) => {
        const isActive = tab.id === activeId;
        return (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            role="tab"
            type="button"
            aria-selected={isActive}
            onClick={() => onSelect(tab.id)}
            className="relative rounded px-3 py-2 text-left transition-colors"
            style={{
              color: isActive ? colors.textPrimary : colors.textMuted,
            }}
          >
            <div className="mono text-[11px] font-bold uppercase tracking-[0.18em]">
              {tab.label}
            </div>
            {tab.sublabel && (
              <div
                className="text-[10px]"
                style={{ color: colors.textMuted }}
              >
                {tab.sublabel}
              </div>
            )}
            {isActive && (
              <motion.span
                layoutId="active-tab-underline"
                transition={motionTokens.springGentle}
                className="absolute inset-x-2 bottom-0 h-0.5 rounded-full"
                style={{ background: colors.playerA }}
              />
            )}
          </button>
        );
      })}
    </nav>
  );
}
