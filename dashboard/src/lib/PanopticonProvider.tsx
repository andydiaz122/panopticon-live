'use client';

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
  type RefObject,
} from 'react';

import {
  clampFrameIdx,
  pickActiveLayoutAtTime,
  pickActiveTransitionForPlayer,
  pickLatestBeforeOrAt,
  pickLatestSignalsPerName,
} from './timeIndex';
import type {
  CoachInsight,
  FrameKeypoints,
  HUDLayoutSpec,
  MatchData,
  NarratorBeat,
  PlayerState,
  SignalSample,
} from './types';

/**
 * PanopticonProvider — the single source of truth for video-clock-slaved state.
 *
 * SPLIT CONTEXTS (PATTERN-046):
 *  - PanopticonStaticContext: refs + getters. NEVER changes after mount.
 *    Consume via `usePanopticonStatic()` from zero-render components (canvas engine).
 *  - PanopticonStateContext: 10Hz-throttled derived state. Re-renders consumers
 *    at ≤10Hz. Consume via `usePanopticonState()` from widgets.
 *
 * ONE rAF LOOP (PATTERN-042):
 *  - Runs every frame.
 *  - Updates refs every tick (no React state touched → zero rerenders).
 *  - Gates state updates with `performance.now() - lastStateUpdateMs >= 100`.
 *    This is the rAF-slaved 10Hz throttle that replaces `setInterval`.
 *
 * BOUNDS CLAMPING (PATTERN-045):
 *  - Every time-indexed lookup goes through clampFrameIdx / pickLatestBeforeOrAt,
 *    which handle empty arrays, out-of-bounds, and scrub-to-end safely.
 */

// ──────────────────────────── Context shapes ────────────────────────────

export interface PanopticonStaticAPI {
  /** Ref to the single `<video>` element. */
  videoRef: RefObject<HTMLVideoElement | null>;
  /** Ref to the cached match_data.json payload. Null until fetch resolves. */
  matchDataRef: RefObject<MatchData | null>;
  /** Path to the video MP4 (passed to `<video src={...}>`). */
  videoSrc: string;
  /** Returns the frame at a given index, bounds-clamped. */
  getFrame: (frameIdx: number) => FrameKeypoints | null;
  /** Returns the clip FPS or null if matchData not loaded yet. */
  getClipFps: () => number | null;
  /** Returns the timestamp of the first hud_layout, or Infinity if none. */
  getFirstLayoutMs: () => number;
}

export interface PanopticonStateAPI {
  /** Fetch lifecycle for the match_data JSON. */
  loadState: 'loading' | 'ready' | 'error';
  /** Human-readable error message, populated when loadState === 'error'. */
  errorMsg: string | null;
  /**
   * Loaded match data (reactive — becomes non-null when loadState turns 'ready').
   * Mirror of `matchDataRef.current`; exposed here so render-time reads are
   * reactive (React 19 lint forbids reading refs during render).
   */
  matchData: MatchData | null;
  /** Current video time in ms, rounded to nearest 100ms. */
  currentTimeMs: number;
  /** Player A's currently-active state (from transitions), null before first transition. */
  activePlayerState: PlayerState | null;
  /** The HUD layout whose [ts, valid_until] brackets currentTimeMs, else null. */
  activeHUDLayout: HUDLayoutSpec | null;
  /** Latest coach insight at or before currentTimeMs, else null. */
  activeCoachInsight: CoachInsight | null;
  /** Latest narrator beat at or before currentTimeMs, else null (unused in Core Trio). */
  activeNarratorBeat: NarratorBeat | null;
  /** Latest signal per signal_name for Player A, keyed by signal_name. */
  activeSignalsByName: Record<string, SignalSample>;
}

// Internal "empty" state before match data loads.
const EMPTY_STATE: PanopticonStateAPI = {
  loadState: 'loading',
  errorMsg: null,
  matchData: null,
  currentTimeMs: 0,
  activePlayerState: null,
  activeHUDLayout: null,
  activeCoachInsight: null,
  activeNarratorBeat: null,
  activeSignalsByName: {},
};

const PanopticonStaticContext = createContext<PanopticonStaticAPI | null>(null);
const PanopticonStateContext = createContext<PanopticonStateAPI>(EMPTY_STATE);

export function usePanopticonStatic(): PanopticonStaticAPI {
  const ctx = useContext(PanopticonStaticContext);
  if (!ctx) {
    throw new Error(
      'usePanopticonStatic must be called inside <PanopticonProvider>',
    );
  }
  return ctx;
}

/**
 * Read the 10Hz-throttled state. Falls back to EMPTY_STATE outside the provider
 * so components remain SSR-safe.
 */
export function usePanopticonState(): PanopticonStateAPI {
  return useContext(PanopticonStateContext);
}

// ──────────────────────────── Provider ────────────────────────────

export interface PanopticonProviderProps {
  videoSrc: string;
  matchDataSrc: string;
  children: ReactNode;
}

export default function PanopticonProvider({
  videoSrc,
  matchDataSrc,
  children,
}: PanopticonProviderProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const matchDataRef = useRef<MatchData | null>(null);

  const [loadState, setLoadState] = useState<'loading' | 'ready' | 'error'>(
    'loading',
  );
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  /** Reactive mirror of matchDataRef — render-safe (React 19 forbids ref reads in render). */
  const [matchData, setMatchData] = useState<MatchData | null>(null);

  // Low-frequency derived state. Updates at ≤10Hz from inside the rAF loop.
  const [derivedState, setDerivedState] = useState<
    Omit<PanopticonStateAPI, 'loadState' | 'errorMsg' | 'matchData'>
  >({
    currentTimeMs: 0,
    activePlayerState: null,
    activeHUDLayout: null,
    activeCoachInsight: null,
    activeNarratorBeat: null,
    activeSignalsByName: {},
  });

  // ── Fetch match_data.json ONCE on mount ──────────────────────────────
  useEffect(() => {
    let cancelled = false;
    fetch(matchDataSrc)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP ${res.status} fetching ${matchDataSrc}`);
        }
        return res.json() as Promise<MatchData>;
      })
      .then((data) => {
        if (cancelled) return;
        matchDataRef.current = data;
        setMatchData(data);
        setLoadState('ready');
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setErrorMsg(err instanceof Error ? err.message : String(err));
        setLoadState('error');
      });
    return () => {
      cancelled = true;
    };
  }, [matchDataSrc]);

  // ── Single rAF loop with 10Hz state gate (PATTERN-042) ───────────────
  useEffect(() => {
    let rafId = 0;
    let lastStateUpdateMs = 0;

    const tick = () => {
      rafId = requestAnimationFrame(tick);

      const video = videoRef.current;
      const data = matchDataRef.current;
      // Bail if video / data not ready yet. Refs are null until first render.
      if (!video || !data) return;

      // 10Hz gate. Skip state-derivation work below until 100ms have passed.
      const now = performance.now();
      if (now - lastStateUpdateMs < 100) return;
      lastStateUpdateMs = now;

      // Compute currentTimeMs (rounded to 100ms to avoid micro-drift rerenders).
      const currentTimeSec = video.currentTime;
      const currentTimeMsRaw = currentTimeSec * 1000;
      const currentTimeMs = Math.round(currentTimeMsRaw / 100) * 100;

      // Derive low-frequency state. All lookups are bounds-safe via helpers.
      const activeHUDLayout = pickActiveLayoutAtTime(
        data.hud_layouts,
        currentTimeMsRaw,
      );
      const activeCoachInsight = pickLatestBeforeOrAt(
        data.coach_insights,
        currentTimeMsRaw,
      );
      const activeNarratorBeat = pickLatestBeforeOrAt(
        data.narrator_beats,
        currentTimeMsRaw,
      );
      const activeTransition = pickActiveTransitionForPlayer(
        data.transitions,
        currentTimeMsRaw,
        'A',
      );
      const activePlayerState = activeTransition?.to_state ?? null;
      const activeSignalsByName = pickLatestSignalsPerName(
        data.signals,
        currentTimeMsRaw,
      );

      // Only call setState if any relevant value changed (identity check is
      // enough — the pick helpers return stable references when the item is
      // unchanged).
      setDerivedState((prev) => {
        if (
          prev.currentTimeMs === currentTimeMs &&
          prev.activePlayerState === activePlayerState &&
          prev.activeHUDLayout === activeHUDLayout &&
          prev.activeCoachInsight === activeCoachInsight &&
          prev.activeNarratorBeat === activeNarratorBeat &&
          shallowEqualSignals(prev.activeSignalsByName, activeSignalsByName)
        ) {
          return prev;
        }
        return {
          currentTimeMs,
          activePlayerState,
          activeHUDLayout,
          activeCoachInsight,
          activeNarratorBeat,
          activeSignalsByName,
        };
      });
    };

    rafId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafId);
  }, []);

  // ── Static context: stable identities across render lifetimes ────────
  const staticApi = useMemo<PanopticonStaticAPI>(
    () => ({
      videoRef,
      matchDataRef,
      videoSrc,
      getFrame: (frameIdx: number) => {
        const data = matchDataRef.current;
        if (!data) return null;
        const clamped = clampFrameIdx(
          frameIdx / data.meta.clip_fps,
          data.meta.clip_fps,
          data.keypoints.length,
        );
        return data.keypoints[clamped] ?? null;
      },
      getClipFps: () => matchDataRef.current?.meta.clip_fps ?? null,
      getFirstLayoutMs: () =>
        matchDataRef.current?.hud_layouts[0]?.timestamp_ms ?? Infinity,
    }),
    // videoSrc is the only input that can change; refs are stable by construction.
    [videoSrc],
  );

  const stateApi = useMemo<PanopticonStateAPI>(
    () => ({
      loadState,
      errorMsg,
      matchData,
      ...derivedState,
    }),
    [loadState, errorMsg, matchData, derivedState],
  );

  return (
    <PanopticonStaticContext.Provider value={staticApi}>
      <PanopticonStateContext.Provider value={stateApi}>
        {children}
      </PanopticonStateContext.Provider>
    </PanopticonStaticContext.Provider>
  );
}

// ──────────────────────────── Helpers ────────────────────────────

/**
 * Shallow equality check for the activeSignalsByName Record.
 *
 * Keys are signal_names (small set, ≤7). Values are SignalSample references
 * returned from `pickLatestSignalsPerName` — identity stability means if the
 * same sample object is the "latest" for a key, we'll get the same reference
 * back on the next call (the source data array doesn't mutate).
 */
function shallowEqualSignals(
  a: Record<string, SignalSample>,
  b: Record<string, SignalSample>,
): boolean {
  const aKeys = Object.keys(a);
  const bKeys = Object.keys(b);
  if (aKeys.length !== bKeys.length) return false;
  for (const k of aKeys) {
    if (a[k] !== b[k]) return false;
  }
  return true;
}
