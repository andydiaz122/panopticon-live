# PANOPTICON LIVE — CV Hackathon Submission Summary

Panopticon Live is a 2K-Sports-style video-game HUD for pro tennis, powered by Claude Opus 4.7. We extract clinical-grade Biomechanical Fatigue Telemetry from standard 2D Broadcast Pixels — no wearables, no sensors. Seven signals: recovery lag, crouch depth, toss precision, ritual discipline, court position, court coverage, reaction timing. All from a single YOLO11m-Pose pass on Apple Silicon, filtered through a Kalman filter that operates on physical court meters.

The engineering moat is a strict 3-Pass DAG with an RTS backward smoother that compresses peak velocity noise by 47 percent against forward-only Kalman on real pro footage.

The Opus 4.7 showcase is a three-agent Opus 4.7 Multi-Agent Swarm — Analytics Specialist, Technical Biomechanics Coach, Tactical Strategist — with real tool use, real extended thinking, real handoffs. To survive Vercel's 15-second serverless timeout, we built Offline Trace Playback: capture the full execution trace during precompute, replay it client-side at baud-rate pacing.

516 tests passing. Solo-built in six days. MIT licensed.

Buyers: broadcasters, sports betting syndicates, elite coaching.
