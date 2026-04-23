---
name: threshold-tuning-debt
description: Calibration discipline for PANOPTICON LIVE — whenever upstream signal processing changes (Kalman variant, SG filter, pose model, RTS vs forward-only), every downstream hardcoded kinematic threshold incurs TUNING DEBT and must be re-tuned empirically against the new amplitude distribution. Use when upgrading any filter/smoother/model that feeds the state machine or signal extractors.
---

# Threshold Tuning Debt

## The core invariant

**A signal extractor's thresholds are calibrated against the AMPLITUDE DISTRIBUTION of its input. If you change the input's amplitude distribution, you have invalidated the thresholds.** Silently. In ways that unit tests CANNOT catch, because unit tests use synthetic paths whose amplitudes you chose.

## When this fires

| Upstream change | What shifts | Downstream victims |
|---|---|---|
| Forward Kalman → RTS smoother | Velocity peaks ~30-40% lower amplitude (jitter stripped) | `state_machine` speed thresholds, `lateral_work_rate` p95, `recovery_latency` movement-onset trigger |
| SG polyorder 1 → 2+ | Impulse peaks PRESERVED (were previously smeared) | `split_step_latency` peak detection, any "push-off" impulse detector |
| Pose model swap (YOLO11m → YOLO11x, or openpose → mediapipe) | Keypoint noise floor shifts | `serve_toss_variance` std-dev, `ritual_entropy` spectral energy |
| dt / fps change | Temporal derivatives scale | EVERY velocity signal, every "delta-per-frame" check |
| Court homography re-calibration | Meters scale shifts | `baseline_retreat_distance_m`, any meter threshold in FSM |

## The tuning protocol (non-negotiable)

1. **Inventory the thresholds**: `grep -rn 'VELOCITY_\|THRESHOLD\|> 0\\.\|< 0\\.' backend/cv/` → every numeric comparison involving velocity, distance, angle, or time. Copy into a spreadsheet: threshold name, file:line, old value, distribution source.
2. **Run the NEW pipeline on a real or synthetic dataset**. Minimum 1 minute of realistic motion. Prefer real broadcast footage.
3. **Histogram the inputs that each threshold gates on**. For each threshold, plot the distribution of the value it compares against during the states/windows where it fires. A well-calibrated threshold sits at a meaningful percentile (often 50th for "normal motion" gates, 90-95th for "unusual event" gates).
4. **Propose new values based on percentiles**, NOT ratios of old-to-new amplitudes. The "divide everything by 1.5 because RTS reduces amplitude by ~33%" heuristic is WRONG — different signals have different reduction ratios depending on which harmonic they extract.
5. **Codify in `backend/cv/thresholds.py`** (create if absent): a single `@dataclass(frozen=True)` module of typed constants. Old values go in git history, not as commented-out lines.
6. **Regression tests**: pin the NEW thresholds with tests that would fail if someone reverts them. Use named constants in both implementation and tests (never raw numbers) so a rename refactors them together.
7. **Document the debt**: note in MEMORY.md which upstream change triggered the retune, when, and the percentile methodology used.

## Anti-patterns

- **Guessing**: "The amplitude dropped ~30% so divide thresholds by 1.3." The ratio varies per signal — Kalman's vx vs. pose's wrist-y have different noise profiles, so RTS affects them differently.
- **Preserving old thresholds because tests pass**: unit tests use synthetic inputs. They pass because you chose inputs that matched the synthetic thresholds. Real data will STARVE.
- **Tuning a single threshold at a time**: thresholds interact via the FSM. If the PRE_SERVE_RITUAL-entry threshold drops but the ACTIVE_RALLY-exit threshold doesn't, you'll get stuck in the wrong state. Tune the FULL set as a coherent block.
- **Skipping the "real data" step**: synthetic motion doesn't capture sensor noise, occlusion clusters, or pose-keypoint dropouts. Tune on actual broadcast footage OR a high-fidelity synthetic path validated by `video-validation-protocol`.

## Contract with `cv-pipeline-engineering`

This skill OWNS the tuning discipline + `backend/cv/thresholds.py` module.
`cv-pipeline-engineering` OWNS the extractors that CONSUME those thresholds.
When an extractor needs a new threshold, it imports from `thresholds.py`; it does NOT hardcode.

## References
- `PATTERN-057` in MEMORY.md (origin pattern entry)
- `PATTERN-053, PATTERN-054, PATTERN-055` (the Kalman RTS upgrade that triggered the first debt repayment)
- `biomechanical-signal-semantics` (where the physical meaning of each threshold is documented)
