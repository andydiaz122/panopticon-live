'use client';

import { useCallback } from 'react';

import { usePanopticonState } from '@/lib/PanopticonProvider';
import { colors } from '@/lib/design-tokens';
import type { SignalSample } from '@/lib/types';

/**
 * Download Match Data CSV — the demo's tangible data artifact.
 *
 * Per DECISION-019, the FINAL PRODUCT is the data-extraction platform that
 * produces downloadable biometric data files. The dashboard is a SHOWCASE.
 * This button exposes the actual product judges can point at and inspect.
 *
 * Output format: long-form tidy CSV (one row per (timestamp, signal_name)).
 *   - Matches the on-disk shape from the precompute pipeline
 *   - Analyst-friendly (R/pandas/Polars all read tidy CSV natively)
 *   - Includes baseline_z_score so anomaly detection is visible per row
 *
 * Pure client-side: Blob → URL.createObjectURL → trigger anchor click.
 * No server roundtrip. Works on every Vercel deploy without API.
 */

const CSV_HEADER =
  'timestamp_ms,match_id,player,signal_name,value,baseline_z_score,state';

const formatRow = (s: SignalSample): string =>
  [
    s.timestamp_ms,
    s.match_id,
    s.player,
    s.signal_name,
    s.value ?? '',
    s.baseline_z_score ?? '',
    s.state,
  ].join(',');

export default function DownloadCsvButton() {
  const { matchData } = usePanopticonState();

  const handleDownload = useCallback(() => {
    if (!matchData) return;
    const csv = [CSV_HEADER, ...matchData.signals.map(formatRow)].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${matchData.meta.match_id}_biometric_signals.csv`;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
  }, [matchData]);

  if (!matchData) return null;

  const rowCount = matchData.signals.length;

  return (
    <button
      type="button"
      onClick={handleDownload}
      className="mono inline-flex items-center gap-2 rounded-sm px-3 py-2 text-[11px] font-bold uppercase tracking-[0.18em] transition-colors hover:opacity-90"
      style={{
        background: colors.bg1,
        color: colors.playerA,
        border: `1px solid ${colors.borderAccent}`,
      }}
      aria-label={`Download biometric signals CSV (${rowCount} rows)`}
    >
      <span aria-hidden="true">↓</span>
      <span>Download Match Data (.csv)</span>
      <span style={{ color: colors.textMuted }}>· {rowCount} rows</span>
    </button>
  );
}
