# Frame Grounding 0-11s (Player A)

Single-pass vision validation per Team-Lead Override (G38 killed — no blind two-pass).
Frames extracted via `ffmpeg -vf "fps=1" -t 12` → `frames/t_0000.jpg` … `t_0011.jpg`.
Validated by `video-frame-validator` agent on 2026-04-24.

Scope: narrow to PLAYER A (near-court). Player B (far-court) mentioned only where his presence informs what Player A is doing (or not doing) — per DECISION-008, this is a single-player product.

| t (s) | Visible action | Confidence | Rally-micro phase |
|---|---|---|---|
| 0 | Player A is NOT visible in near court. Player B stands near far baseline (yellow shirt). "BREAK POINT" overlay visible on scoreboard. | 0.90 | DEAD_TIME |
| 1 | Player A still off-camera at near court; Player B stationary at far baseline. | 0.85 | DEAD_TIME |
| 2 | Player A off-camera at near court; Player B stationary at far baseline. | 0.85 | DEAD_TIME |
| 3 | Player A not yet in near court; court empty at near end. | 0.85 | DEAD_TIME |
| 4 | Player A off-camera in near court; Player B shifts slightly along far baseline. | 0.85 | DEAD_TIME |
| 5 | Player A off-camera in near court. Scoreboard "BREAK POINT" indicator has cleared. | 0.80 | DEAD_TIME |
| 6 | Player A off-camera in near court; Player B adjusts position on far baseline. | 0.80 | DEAD_TIME |
| 7 | Player A off-camera in near court; Player B stands near far baseline center. | 0.80 | DEAD_TIME |
| 8 | Player A off-camera in near court; Player B holds position on far baseline. | 0.80 | DEAD_TIME |
| 9 | Head and dark shoulder of Player A begin to appear at the very bottom edge of frame, entering from below the baseline. | 0.60 | DEAD_TIME (transitioning) |
| 10 | Player A visible near the bottom-left baseline area, torso and legs shown, back toward camera, mid-stride walking forward onto court; racket in right hand at hip level, orange/red strings visible. | 0.85 | PRE_SERVE_RITUAL |
| 11 | Player A stands just behind baseline, left arm raised near head (toss motion), right arm extended with racket face open; yellow ball visible in air at waist/racket level. Back partially to camera. | 0.70 | SERVE |

## Key authoring implications

1. **Plan A3 row for t=0 ("Player A enters court")** — **REVISED**: Player A is off-camera for most of 0-9s. The live broadcast is showing the between-point moment after a break-point situation. Narration must acknowledge this (either focus on the scoreboard tension, Player B's waiting posture, or future-tense setup for the server's motion).

2. **Plan A3 row for t=11 ("biometric_hook=split_step_latency_ms")** — **REVISED**: at t=11 Player A is the SERVER, not the returner. `split_step_latency_ms` is a returner-side signal (gate requires detecting a bounce and then the receiver's reaction). Not a valid hook for this frame.

3. **State grid** (state_grid_0_11s.json) — use DEAD_TIME, not WARMUP, for 0-9s. This is mid-match break-point dead time, not match-warmup. Transition to PRE_SERVE_RITUAL at t=9000ms (when Player A enters frame and starts walking to baseline), to SERVE at t=10500ms (start of toss motion per the t=11 frame), to ACTIVE_RALLY at t=11200ms (ball contact; matches live FSM's own t=11200ms transition).

4. **Player identity** — the v4 plan drafted "Hubert Hurkacz" as an example profile, but the actual UTR-clip player identity was not verified at authoring time. `player_profile.json` was rewritten to an anonymized-but-rich shape (`name: "UTR Pro A"`, no fabricated ATP numerics, qualitative fields restricted to visually-observable evidence from frames t_0010.jpg / t_0011.jpg). The dynamic identity injection in `_build_baseline_context` still fires because `name` is non-null, and the Scouting Committee will reference the player by profile name rather than the generic `Player A` fallback.

5. **Every narration timestamp is now backed by a frame** — the narration copy in `narrations_0_11s.json` only describes what is visible in the referenced frame, per Citadel rigor.
