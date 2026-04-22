---
name: topological-identity-stability
description: Absolute Court Half Assignment for PANOPTICON LIVE — the anti-identity-swap pattern for robust Player A/B attribution. Use when building or reviewing backend/cv/pose.py or any CV code that distinguishes near vs far player. Canonical answer to USER-CORRECTION-007.
---

# Topological Identity Stability

Identity-swap is the CV pipeline's most insidious failure mode: signals attributed to Player A actually belong to Player B (or a ballboy), and Kalman tracks rubber-band across the court. This skill documents the ONLY acceptable identity-attribution algorithm in PANOPTICON LIVE.

## The Rejected Approaches (and why)

### Hungarian Assignment on Euclidean Distance
❌ When a ballboy runs behind a player, the tracker can swap IDs based on proximity.

### Top-2 by Overall Confidence, Sort by Y
❌ If Player B is occluded by the net, their YOLO confidence drops. A linesman or ballboy with higher confidence takes Player B's slot. Sorting by Y then assigns the ballboy to Player B's identity.

### IoU Tracking Across Frames
❌ Fragile under occlusions; frame-to-frame continuity assumptions break when either player briefly leaves the court polygon.

## The Canonical Approach: Absolute Court Half Assignment

The tennis court is 23.77m long. The net is at the midpoint: **Y = 11.885 m** in physical court coordinates. A tennis player does not cross the net mid-rally. These two facts provide a topologically stable identity partition.

```python
NET_Y_M: float = 23.77 / 2  # exactly 11.885

def assign_players(
    raw_detections: list[RawDetection],
    court_mapper: CourtMapper,
) -> dict[PlayerSide, PlayerDetection | None]:
    # Step 1: compute robust foot point for every raw detection
    # (ankle -> knee -> hip fallback per USER-CORRECTION-003)
    enriched: list[EnrichedDetection] = []
    for d in raw_detections:
        feet_mid_xyn = robust_foot_point(d.keypoints_xyn, d.confidence)
        feet_mid_m = court_mapper.to_court_meters(feet_mid_xyn)
        if feet_mid_m is None:
            continue  # off-court; discard entirely
        enriched.append(
            EnrichedDetection(
                raw=d,
                feet_mid_xyn=feet_mid_xyn,
                feet_mid_m=feet_mid_m,
                mean_confidence=float(np.mean(d.confidence)),
            )
        )

    # Step 2: split by absolute court half
    near_half = [e for e in enriched if e.feet_mid_m[1] > NET_Y_M]  # Player A
    far_half  = [e for e in enriched if e.feet_mid_m[1] <= NET_Y_M]  # Player B

    # Step 3: highest-confidence detection within each half
    player_a = max(near_half, key=lambda e: e.mean_confidence, default=None)
    player_b = max(far_half,  key=lambda e: e.mean_confidence, default=None)

    return {
        "A": to_player_detection(player_a, "A") if player_a else None,
        "B": to_player_detection(player_b, "B") if player_b else None,
    }
```

## Coordinate Convention

When we project court corners via homography, we fix the orientation:
- Top-left corner of the frame maps to (0, 0) in court meters
- Top-right corner maps to (court_width_m, 0)
- Bottom-right maps to (court_width_m, court_length_m = 23.77)
- Bottom-left maps to (0, court_length_m)

Therefore:
- **Near player** (bottom of frame, camera-close) has **large y_m** (close to 23.77)
- **Far player** (top of frame, camera-far) has **small y_m** (close to 0)
- **Net** is exactly at y_m = 11.885

This convention is frozen. Do not flip. Tests enforce it.

## Why This Is Immune to the Failure Modes

| Attack | Why it fails against Court Half Assignment |
|---|---|
| Ballboy steps inside court on Player A's side | They're competing only within Player A's half. If Player A is still detected with high conf, they win. If Player A is briefly out of frame, the ballboy is the wrong identity for one frame; Kalman occlusion coasting handles the absence gracefully. |
| Net occludes Player B's ankles | `robust_foot_point` falls back to knees → hips (USER-CORRECTION-003). Player B's confidence drops but they're the ONLY detection in the far half (ballboys usually aren't on the far half during serve). No swap possible. |
| Two players same Y in screen space | Cannot happen: they are on opposite sides of the net in physical court meters. |
| Linesman standing near sideline | In-polygon filter excludes them (they stand on the sideline, outside the play rectangle). |

## Failure Modes NOT Handled (acceptable for hackathon)

- Doubles: 4 players, 2 per half. Our rule picks top-1 per half, so we'd lose the partner. Assumption: all UTR clips are singles.
- Ball-machine training: single player plus a bouncing machine. Assumption: real match footage.
- Mid-set court switch (odd-game changeover): players swap halves. The state machine will be in DEAD_TIME during changeover, so signal extraction is gated out anyway. Attribution re-stabilizes as soon as the next serve begins.

## Integration Points

- `backend/cv/pose.py::PoseExtractor.infer()` returns `dict[PlayerSide, PlayerDetection | None]` using this function
- `tests/test_cv/test_pose.py` has fixtures validating: ballboy-in-near-half + occluded-far-player → ballboy does not get B's identity
- `backend/cv/kalman.py` runs one `PhysicalKalman2D` per side (A and B); if `assign_players` returns None for a side, that side's Kalman coasts
- `backend/cv/state_machine.py` runs one FSM per side; coupled via match-level sync per `match-state-coupling` skill

## Test Cases (must be in tests/test_cv/test_pose.py)

1. **Baseline**: 2 in-court detections, one in each half → assigned correctly, stable across frames
2. **Ballboy in near half + occluded far player**: near-half top-1 is Player A (even if ballboy is a detection, Player A is real player), far-half top-1 is Player B despite low confidence → no swap
3. **Only one player detected (singles warmup)**: near half has 1, far half has 0 → returns `{"A": player, "B": None}`
4. **Both halves empty** (crowd shot): returns `{"A": None, "B": None}`
5. **Changeover-style flip** (two players on near side): the lower-Y of them still sits in the near half technically, but if both `y_m > 11.885`, one wins A and the other is discarded. No false attribution.
6. **Bleacher detections**: filtered out before half-splitting via `is_in_court_polygon`
