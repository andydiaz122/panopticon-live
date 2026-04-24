# Tennis CV Competitor Audit — PANOPTICON LIVE

**Date**: 2026-04-24
**Method**: Perplexity scouting pass (4 calls, ≤5 budget). Source: vendor pages, press, ITF approval reports, academic papers (PMC / arXiv / Stanford), trade press (tennis.com, sportstech blogs).
**Scope**: 6 primary commercial competitors + 2 academic SOTA references. NOT institutional analysis — gaps noted where details paywalled.

---

## TOP-OF-REPORT SYNTHESIS (≤150 words)

**1. The data moat is biomechanical fatigue telemetry from broadcast pixels — and nobody else has it.** Every commercial competitor extracts BALL-and-OUTCOME signals (speed, placement, spin, in/out, rally length, heat maps). PlaySight, swing.vision, Baseline Vision, Hawk-Eye SkeleTRACK all stop at *macro outcomes* or *single-stroke biomechanics* (knee bend on serve, shoulder-over-shoulder angle). None extract our 7 fatigue signals — recovery latency, serve-toss variance, ritual entropy, crouch-depth degradation, baseline retreat, lateral work rate, split-step latency. Hawk-Eye SkeleTRACK is the closest analog but requires 10-camera stadium installs at $$$, is fed to broadcasters/teams, NOT fans, and measures geometry not temporal-decay patterns.

**2. The ONE signal nobody else measures: *ritual entropy* (between-point pre-serve routine variance).** Every system literally EDITS DEAD TIME OUT (swing.vision, PlaySight). They throw away the exact frames where fatigue lives.

**3. UX pattern to STEAL**: PlaySight/swing.vision's heat-map-driven post-match dashboard. **UX pattern to SUBVERT**: their "edit out the boring parts" reflex. We make the boring parts the hero — between-point biomechanics IS the show.

**4. Positioning narrative**: "Hawk-Eye for fatigue" or "Bloomberg Terminal for the 70% of tennis nobody films." Demo opens with: *"Every system in tennis tells you what already happened. We tell you what's about to break."*

**5. Pricing whitespace**: Consumer ($15/mo swing.vision) vs Enterprise (Hawk-Eye, six-figure stadium installs) — gap in the middle for *broadcast-overlay-as-fan-product*. Our deployment model (broadcast-pixel CV, no court hardware) is structurally cheaper than every install-based competitor.

---

## COMPETITOR MATRIX

### 1. swing.vision (PRIMARY TARGET)

| Field | Detail |
|---|---|
| **URL** | https://swing.vision/ |
| **Signals extracted** | Ball speed (avg from contact-to-bounce, 20% under radar), shot placement, shot type (forehand/backhand/serve), spin type (topspin/slice/flat), rally length, court positioning heat-maps, line-call in/out, serve depth/accuracy. ITF-approved per PAT-25-037 report. |
| **Signals NOT extracted (our differentiator)** | Recovery latency, serve-toss variance, ritual entropy, crouch-depth degradation, baseline retreat distance, lateral work rate, split-step latency, ANY fatigue-decay metric, ANY between-point biomechanics. The ITF report explicitly lists what they record: ball location 3D, shot type, spin type, ball speed — that's it. **They actively edit dead time OUT, throwing away the exact frames our system mines.** |
| **Deployment model** | Broadcast-pixel CV (single-camera iPhone/iPad mounted at back of court at 60fps), local ML inference on-device + WiFi/cellular sync to backend, optional Apple Watch & on-court tablet. Patented, ITF-approved Player Analysis Technology. |
| **UX direction** | Post-match heat-map / charts dashboard, dead-time-edited highlight reels (auto-trim 2.5h match → 17 min), shot-by-shot filter, real-time line-call challenges via Apple Watch, "personalized coaching after each session," weekly-goal nudges. Built by ex-Tesla/Apple AI engineers. Backed by Andy Roddick + Lindsay Davenport. |
| **Pricing tier** | **Consumer.** Free tier (2hr tracking + analysis), Pro subscription unlocks line calling, automated scoring, unlimited storage. Official Player & Ball Tracking app of Tennis Australia, LTA, ITA. |
| **Differentiator vs PANOPTICON** | swing.vision = "everyone's racquet-sport stats coach" for amateur self-recorded video. PANOPTICON = "Hawk-Eye for fatigue" on professional broadcast pixels with biomechanical fatigue telemetry they explicitly discard. Different deployment context, different signals, different audience. |

---

### 2. Hawk-Eye Innovations (incl. SkeleTRACK)

| Field | Detail |
|---|---|
| **URL** | https://www.hawkeyeinnovations.com/ |
| **Signals extracted** | Classic Hawk-Eye: ball trajectory via 10-camera stadium triangulation @ 340fps, ELC line-calling (3.6mm avg error, <5mm at landings per Australian Open Vicon validation). **SkeleTRACK** (debuted Laver Cup 2024): 29 skeletal keypoints + 7 racket points → real-time biomechanics: knee-bend angle, shoulder-over-shoulder serve angle, top sprint speed, on-balance %, racket velocity/spin. Generates "kicks/throws/catches" event detection. |
| **Signals NOT extracted (our differentiator)** | SkeleTRACK is the closest commercial analog to PANOPTICON and the strongest competitor on biomechanics. BUT its public-disclosed metrics are **single-instant geometry** (one knee angle, one shoulder angle, one top sprint speed) — NOT temporal-decay patterns or between-point ritual variance. No public mention of recovery latency, ritual entropy, crouch-depth degradation over time, split-step latency, or fatigue-trajectory analytics. Data delivered to broadcasters & coaching teams, not fans. |
| **Deployment model** | Multi-camera stadium install (10+ cameras for tennis), gantry/tripod mounted, calibration-heavy, real-time 3D triangulation. Owned by Sony. |
| **UX direction** | Broadcast graphics overlay (ATP/WTA TV feeds), back-end data feed to teams. NO consumer app. Powers IBM SlamTracker downstream. "Live ELC since 2017 Next Gen Finals" + "10,000+ Court Days" in tennis. |
| **Pricing tier** | **Enterprise / institutional only.** Six-figure+ stadium installs, federation contracts (Wimbledon, US Open, ATP Tour, Laver Cup). |
| **Differentiator vs PANOPTICON** | Hawk-Eye = ground truth for elite stadiums; PANOPTICON = same signal class extracted from any broadcast pixel without 10-camera install. AND: PANOPTICON's 7 fatigue signals are temporal/decay patterns Hawk-Eye doesn't publicly extract. We are "Hawk-Eye for the rest of tennis + the metrics they don't bother computing." |

---

### 3. Sportradar Tennis

| Field | Detail |
|---|---|
| **URL** | https://www.sportradar.com/ |
| **Signals extracted** | Ball-by-ball point-level scoring data, betting odds feeds, statistical match metadata, momentum metrics. Aggregator/distributor of OFFICIAL data feeds from federations (ATP/WTA/ITF), NOT a CV vendor in tennis. Public details paywalled behind sales. |
| **Signals NOT extracted (our differentiator)** | No proprietary biomechanical extraction; no pose estimation; no fatigue telemetry. They redistribute official scoring + odds, not raw video signals. |
| **Deployment model** | Data feed / API platform — they ingest from on-court providers (Hawk-Eye, federation data) and distribute to bookmakers, broadcasters, fantasy. |
| **UX direction** | B2B dashboards, betting widgets, broadcaster overlays. No fan-facing biomechanics product. |
| **Pricing tier** | **Enterprise only.** Federation-licensed data feeds, sportsbook contracts. |
| **Differentiator vs PANOPTICON** | Sportradar sells *what happened* (scores, betting markets); PANOPTICON shows *what's about to break*. Different layer of the stack — they're a data distributor, we're a signal extractor. Could become a downstream customer, never a head-to-head competitor. |

---

### 4. TrackMan Tennis

| Field | Detail |
|---|---|
| **URL** | https://www.trackman.com/ (tennis vertical) |
| **Signals extracted** | Doppler radar-based ball measurements: ball speed, spin axis, spin rate, launch angle, landing position, trajectory in 3D. Same radar-physics platform as TrackMan golf/baseball. |
| **Signals NOT extracted (our differentiator)** | NO player pose, NO biomechanics, NO fatigue telemetry — radar tracks the BALL. Player skeletal data is structurally absent from the deployment model. |
| **Deployment model** | Doppler radar hardware install at courtside/stadium. Hybrid hardware/software. |
| **UX direction** | Coaching app with shot-by-shot ball physics dashboards. Used in elite-academy training (junior development, college). |
| **Pricing tier** | **Enterprise / academy** — high-end hardware, federation/academy contracts. Higher per-install cost than swing.vision. |
| **Differentiator vs PANOPTICON** | TrackMan = ball physics ground truth; PANOPTICON = player physiology. Orthogonal data classes — could co-exist, never substitute. |

---

### 5. IBM Watson SlamTracker (Wimbledon / US Open / Roland Garros)

| Field | Detail |
|---|---|
| **URL** | https://www.wimbledon.com/slamtracker (also USOpen.org, RolandGarros.com) |
| **Signals extracted** | Real-time match scoring, point-by-point timeline, momentum charts, "Likelihood to Win" projection (refreshed each game), Match Chat (2025) — generative AI fan Q&A built on watsonx + IBM Granite + RAG over Wimbledon editorial style. **Consumes Hawk-Eye data downstream**, doesn't extract its own. |
| **Signals NOT extracted (our differentiator)** | Zero biomechanical signals. SlamTracker is a fan-engagement layer over MATCH-LEVEL aggregates (break points, holds, points won). The "AI" is conversational + win-probability modeling, NOT computer vision. |
| **Deployment model** | Tournament-scoped web/app product. AI-as-narrator over Hawk-Eye-derived match data. |
| **UX direction** | **Closest UX neighbor to PANOPTICON's positioning** — fan-facing AI commentary + interactive Q&A during live play. "Match Chat" answers natural-language questions ("who's converted more break points?"). Win-probability chart updates per game. |
| **Pricing tier** | **Free to fans** during the four Grand Slams; IBM monetizes via the AELTC/USTA/FFT/TA enterprise contracts. |
| **Differentiator vs PANOPTICON** | SlamTracker = LLM commentary over scoreboard data; PANOPTICON = LLM commentary over biomechanical fatigue signals nobody else has. We are "SlamTracker if SlamTracker had a body." Strong positioning anchor — judges recognize SlamTracker. |

---

### 6. PlaySight SmartCourt

| Field | Detail |
|---|---|
| **URL** | https://playsight.com/our-sports/tennis/ |
| **Signals extracted** | Multi-angle video, automated highlights, ball/player tracking, serve-and-stroke tagging by type/speed/spin, 3D shot map, court positioning, "biomechanical analysis" tools (slo-mo + audio annotation, NOT automated pose extraction). SmartTracker autonomous PTZ camera control. |
| **Signals NOT extracted (our differentiator)** | Despite the "biomechanical analysis" marketing, the actual product is *manual frame-by-frame coach review with audio annotations* — no automated 7-fatigue-signal extraction, no recovery latency, no ritual entropy, no crouch-depth tracking. Closer to "DVR for coaches" than to PANOPTICON. |
| **Deployment model** | Permanent multi-camera court install ("connected camera platform") — SmartCourt fixed venue, OR portable LiveU partnership. |
| **UX direction** | Coach/team-focused video review tool, AI-generated highlights, "TagMe" social-share clips, mobile-app multi-angle replay, streaming/broadcast for sub-elite venues. Customers: IMG Academy, NBA teams, USTA National Campus, 80+ NCAA programs. |
| **Pricing tier** | **Hybrid consumer/enterprise.** Per-court SmartCourt Pro install fees + subscription. $26M raised (SoftBank, Verizon Ventures, Greg Norman). Targets clubs/academies/colleges, not individual amateurs. |
| **Differentiator vs PANOPTICON** | PlaySight = installed-camera DVR + auto-highlights + slo-mo coach review. PANOPTICON = pixel-level fatigue extractor with no court hardware. PlaySight needs a $20k+ install; we need a YouTube URL. |

---

### 7. Baseline Vision (Tel Aviv) — additional commercial entrant

| Field | Detail |
|---|---|
| **URL** | https://www.baselinevision.com/ |
| **Signals extracted** | Ball 3D trajectory (5% error), bounce position, ball speed (5% error), shot type (forehand/backhand/etc.), 2D player position, rally length, net clearance per shot. Real-time line calling with audio + LED feedback. ITF-PAT approved. |
| **Signals NOT extracted (our differentiator)** | Same as swing.vision — ball-and-outcome, no biomechanical fatigue telemetry. No pose estimation product disclosed. |
| **Deployment model** | Two-camera 4K@60fps unit clamped to net post in 20 seconds — no electricity, no WiFi required, on-device processing, 8GB RAM, 256GB storage, 5h battery. |
| **UX direction** | Net-post hardware + mobile app for drills, line-calling visualization, gamified challenges, social sharing. Strong portability positioning — "the tech used by elite pros, now on every court." |
| **Pricing tier** | **Prosumer / club.** Hardware + app. 650+ units deployed in 25+ countries. 10 national federations as customers. |
| **Differentiator vs PANOPTICON** | Baseline Vision = portable two-camera hardware for ball tracking + line calls. PANOPTICON = pure software extracting biomechanics from any broadcast feed. Hardware vs software-on-pixels split. |

---

## ACADEMIC SOTA (8) — research-only, not commercial competitors but signal-class reference

### Emmerson et al., *PLoS One* 2026 (Univ. of Bath / CAMERA)

| Field | Detail |
|---|---|
| **URL** | https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0345913 |
| **Signals extracted** | **Mechanical work as a fatigue indicator** — markerless motion capture (multi-camera) → OpenSim inverse kinematics → CoM-based external/internal mechanical work, validated against neuromuscular fatigue (peak forward CoM velocity reduction). Pooled correlation r ≈ −0.93 between work done and fatigue. |
| **Signals NOT extracted vs PANOPTICON** | This paper VALIDATES the upstream physics (mechanical work IS a valid fatigue proxy), but uses lab-grade markerless mocap + OpenSim IK. It does NOT cover ritual entropy, serve-toss variance, between-point recovery latency, crouch-depth degradation, or the 5 other PANOPTICON signals. **It does, however, validate that our "mechanical work" intuition (lateral work rate signal) is academically sound** — this is a citation we should leverage in the demo / repo README. |
| **Deployment model** | Research lab markerless mocap (multi-cam, calibrated, OpenSim post-processing). Not deployable to broadcast. |
| **Pricing tier** | **Research only.** Open-access publication. |
| **One-line takeaway for PANOPTICON** | Cite this paper as scientific validation of the lateral-work-rate signal. They ran the controlled experiment; we operationalize the insight on broadcast pixels. |

### Vishal Tiwari et al. (BMVC tennis analytics) + AlShami Pose2Trajectory + various 2024-2025 YOLO+pose pipelines

| Field | Detail |
|---|---|
| **URL** | https://vishaltiwari.github.io/bmvc-tennis-analytics/, https://arxiv.org/html/2603.13397v2, https://arxiv.org/html/2507.02906v1, https://stanford.edu/class/ee367/Winter2025/report/report_Jeffrey_Liu.pdf |
| **Signals extracted** | YOLO/MediaPipe pose + ball tracking, shot classification (FH/BH/serve/ready), wrist-trajectory comparison vs pro, basic court-keypoint homography, "player reaction time" (defined as frames-to-significant-displacement after opponent shot). |
| **Signals NOT extracted vs PANOPTICON** | None of these academic pipelines extract the 7-signal fatigue suite. The closest is "player reaction time," which overlaps with our recovery_latency definition — but NO paper extracts ritual entropy, serve-toss variance, crouch-depth degradation, or treats fatigue as a temporal decay phenomenon. They mostly stop at single-stroke biomechanics or shot classification. |
| **Deployment model** | Research pipelines / Stanford coursework, single-camera broadcast or amateur footage. |
| **Pricing tier** | **Research / open-source.** GitHub repos, no commercial product. |
| **One-line takeaway for PANOPTICON** | Confirms we have whitespace — the academic CV community has converged on FH/BH/serve classification + ball tracking, NOT on fatigue telemetry. We are extending the academic frontier, not lagging it. |

---

## STRATEGIC IMPLICATIONS FOR DEMO NARRATIVE

1. **Open the demo with the discard frame.** Cut to a 2-second clip of swing.vision/PlaySight's "auto-edit dead time" feature, then say: *"That's where every fatigue signal lives. They throw it away. We mine it."* This is the story.

2. **Anchor on Hawk-Eye SkeleTRACK as the closest competitor and beat it on three axes**: (a) PANOPTICON works on any broadcast pixel — no 10-camera stadium install; (b) PANOPTICON measures *temporal decay patterns*, not single-instant geometry; (c) PANOPTICON is fan-facing, SkeleTRACK is broadcaster/team-only.

3. **Position SlamTracker as our UX inspiration**, not our competitor. "Match Chat asks what already happened. Panopticon Live tells you what's about to break."

4. **The "ritual entropy" signal is the headline metric.** Nobody else in the world commercially extracts it. It's also the most VISUALLY interesting (between-point routine variance — judges can SEE the routine breaking down on screen). Lead the demo with this signal, not crouch depth.

5. **Pricing whitespace narrative** (if asked in Q&A): consumer apps are $15/mo for ball stats; enterprise installs are six figures for ball+pose. PANOPTICON sits in the middle — *broadcast-overlay-as-fan-product* with no court hardware — at a price point that doesn't yet exist.

---

## GAPS / OPEN QUESTIONS (for follow-up if time permits)

- TrackMan tennis: signals list is from radar physics datasheets — confirm no recent skeletal/biomechanics product launched in 2025-2026.
- Sportradar: confirm via direct site visit they don't have a "Sportradar Computer Vision" product extending into tennis pose (they do operate one in soccer).
- Hawk-Eye SkeleTRACK: 29-keypoint output IS public, but the *temporal-fatigue analytics* layer they may build on top is not disclosed. Worth re-scouting before a public launch.
- Tenniix (CES 2026 vision-based AI tennis robot, $699) — adjacent category (training robot, not analytics) but worth a glance for fan-facing UX cues.
