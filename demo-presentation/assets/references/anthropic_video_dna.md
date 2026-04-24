# Anthropic Release-Video Design DNA — Reverse-Engineered Cheatsheet

**Source videos** (both downloaded + frame-sampled 2026-04-24):
- `dPn3GBI8lII` — *Introducing Claude Opus 4.6* (39s, 24fps, 1280x720, uploaded 2026-02-05, 367K views)
- `rBJnWMD0Pho` — *Let Claude handle work in your browser* (95s, 30fps, 1280x720, uploaded 2025-12-18, 340K views)

Raw frames live in `/tmp/anthropic_frames_v1/` (26 PNGs) and `/tmp/anthropic_frames_v2/` (32 PNGs). Info JSON + full webm archived in `/tmp/anthropic_dPn3GBI8lII.{webm,info.json}` and `/tmp/anthropic_rBJnWMD0Pho.{webm,info.json}`.

---

## Design DNA in Five Sentences

Anthropic's release aesthetic is **editorial print layout set in motion on cream paper, restrained to the brink of austerity** — warm off-white (#E0D8C8 sandstone for product films / #F8F8F8 near-white for model films) backgrounds, the Claude Spark coral (#D97757 family, measured ≈ #D07050 on screen) deployed as the *only* saturated accent, and a classical transitional serif (headline display, likely Copernicus/Tiempos in the "Opus 4.6" wordmark family) paired against a humanist sans for UI chrome and captions. The two videos invert pacing strategy deliberately: Opus 4.6 is a **77-cuts-per-minute social-proof montage** (tweets, newspaper clippings, chalkboards, brain MRIs, handmade sweaters) designed to blur into one feeling of cultural gravitational pull; Claude for Chrome is a **calm 7-cuts-per-minute workflow narrative** (~8.6s dwell per shot) where a cream-colored hand-cursor walks the viewer through three real browser tasks. Both films share the same grammar: no voiceover, music-only scoring, the Claude Spark appearing only at the moment of "click / send / ship," and a closing wordmark on full-bleed cream that always reads `[Spark icon] Claude` or `Opus 4.X by ANTHROPIC` in that exact sequence. The craft signal is what they *refuse* to do — no gradient fills, no glassmorphism, no drop shadows except subtle window chrome, no inline UI animation curves you can name — which is itself a strong statement that reads as "secure in our intelligence, we do not need to sell you with motion." Steal the palette and the typography hierarchy; steal the restraint even harder.

---

## 1. Color Palette (hex-confirmed from frame sampling)

| Role | Hex (measured) | Canonical | Notes |
|---|---|---|---|
| Primary background — "paper" (Opus film) | #F8F8F8 | #FAF9F5 cream | Warmer off-white, never pure white |
| Primary background — "sand" (Chrome film) | #E0D8C8 | "Anthropic sandstone" | Noticeably warmer/tanner than the model-announcement cream; I'd call this the *product* background and cream the *model* background |
| Primary ink (body + wordmarks) | #101018 – #202020 | #141413 deep slate | True black avoided; always a warm near-black |
| Hero accent — Claude Spark | #D07050 (measured) | #D97757 / #CC785C | Coral/terracotta. Appears on: send buttons, "Claude" icon, slide-comment chips, italic display emphasis ("*actually*") |
| Secondary panel fill (Chrome window chrome) | #F8F8F0 / #F0F0F0 | — | Slightly cooler than sand bg — creates depth without shadow |
| Terminal slate (Claude Code only) | ~#1A1A24 | — | A purple-tinged deep slate used exclusively for the Claude Code terminal window |

**Hard rule observed**: exactly one saturated color on screen at any time, and it is always the Spark coral. No blues, no greens, no other oranges. The rare exception is third-party UI embedded in the browser demo (revenue dashboard's purple chart, Google Docs' blue), which Anthropic deliberately *under-saturates* via the sandstone bg to keep coral as the hero.

---

## 2. Typography

**Headline / display** — A classical transitional serif (stressed "o", pronounced bracketed serifs, moderate contrast). Strongly suggests **Copernicus** or **Tiempos Headline** (Anthropic's known display family). Used for:
- Wordmark transitions: `Opus 4.5` → `Opus 4.6` → `Opus 4.6 by ANTHROPIC`
- Mid-film callouts: `Introducing Opus 4.6`, `Opus 4.6 is remarkably capable.`
- Scene titles in Chrome film: `Pull context from anywhere`
- Ambient product copy shown inside Chrome demos: `Website analytics that *actually* make sense.` — note the italic for emphasis, a signature Anthropic move

**UI chrome / captions** — A humanist sans (likely **Styrene B** or the newer custom "Claude Sans"). Used for:
- Tweet/Instagram post overlays
- Browser UI (tabs, toolbar, doc body)
- Captions like `Most people: I use Claude to vibe code.`

**Monospace** — A generic system mono inside the Claude Code terminal frame. Not a custom face.

**The "ANTHROP\C" wordmark** — the trademark slashed-A letterform appears on the final card. It is a custom geometric sans, all caps, extended tracking — NOT the same face as the body display serif. Use the official SVG (you already have `claude_logo_slate_OFFICIAL.svg` in this folder).

**Hierarchy tell**: body copy is small relative to background. A lot of air. The "Pull context from anywhere" headline occupies maybe 6% of the frame height — the other 94% is sand. Anthropic's layout is generous with margin to the point of feeling editorial.

---

## 3. Motion & Pacing — THE KEY INSIGHT

The two films invert pacing intentionally. Steal the one that matches your scene intent:

### Opus 4.6 film (model launch → "cultural gravity")
- **~50 scene cuts in 39 seconds = 77 cuts/minute = avg 0.78s per shot**
- First 15 seconds is a collage storm: newspaper front page → chalkboard with math → sheep-sweater woman → Mars rover → brain MRI → water pipes → frontend code carousel
- Each tweet overlay pops in for ~0.5s, just long enough to read the handle + caption
- The cuts are HARD CUTS (no crossfades). Some are scale-warp reveals (the "Opus 4.5" card zooms out to reveal the "Opus 4.6" card nearby).
- Rhythm is set by the background music beat — nearly every cut lands on a downbeat
- Ends with ~4 seconds of held silence on the `Opus 4.6 by ANTHROPIC` card (stillness as punctuation after storm)

### Chrome film (product demo → "calm capability")
- **~11 scene cuts in 95 seconds = 7 cuts/minute = avg 8.6s per shot**
- Each shot is one complete workflow beat: (1) empty doc on cream bg, (2) Chrome with tabs opened, (3) Claude sidebar typing the prompt, (4) doc filling with output, (5) scroll to reveal finished doc
- Transitions are HARD CUTS but feel calm because each preceding shot was held long enough to resolve
- A cursor literally walks across the screen — it's not clicking UI elements so much as *modeling confident navigation*. The cursor itself is drawn, possibly post-composited, always with a small coral/coral-tinted glove mitten at its tip — it's branded
- Ends with a `[Spark] Claude` wordmark fade-up + `Visit claude.com/chrome` — held ~5s

### Motion primitives observed (steal these directly)
- **Typewriter reveals**: when text is added to the Claude sidebar, it appears word-by-word at normal typing speed (no fake-fast acceleration) — implies React-side reveal with ~60ms per character
- **Scale-in pops**: the "Introducing" label appears at scale ~0.9 and springs to scale 1 over ~200-300ms (moderate stiffness spring, slight overshoot)
- **Cross-dissolve on wordmarks only**: the `Opus 4.5 → Opus 4.6` transition looks like the "4.5" scales down + fades while "4.6" scales up + fades in the adjacent slot. Duration ~400-500ms. Ease-out.
- **No parallax, no kenburns, no subtle drift**: the frames are static. Motion happens *inside* UI mockups (browser tabs opening, docs scrolling), not applied *to* frames as a cinematographic effect.

---

## 4. Framing & Composition

- **Full-bleed backgrounds, centered subjects**: the Chrome window in V2 sits dead-center with generous sand margin on all sides. The browser chrome is scaled down (maybe ~70% frame width) so the cream background reads as a picture-matte.
- **Editorial stack** in wordmark frames: small label above (`Introducing`), big headline below (`Opus 4.6`), with a peek of a UI collage bleeding in from the right edge — that collage-bleed is a signature move, it hints at "there's more context just off-frame"
- **Social posts always handheld-feeling**: tweet overlays in V1 are rotated a fraction of a degree (maybe ±0.5°), positioned off-grid, drop-shadowed subtly. They feel pasted-on, not rendered-in.
- **Hero / sidekick framing**: in V2, the Claude sidebar is always on the *right*, in a vertical strip of panel fill, with the work happening on the left. Never the reverse.

---

## 5. Transitions (Inventory)

| Type | Where used | Duration |
|---|---|---|
| Hard cut | 95% of cuts in both films | 0ms |
| Scale-warp reveal | `Opus 4.5 → Opus 4.6` wordmark swap | ~400ms |
| Word-by-word typewriter | Any text appearing in Claude sidebar | ~60ms/char |
| Fade-up from black | Never observed. Anthropic doesn't fade from black. |
| Crossfade | Observed ONCE, on the collage-to-wordmark transition in V1 | ~200ms |
| Mask reveal / wipe / slide | Not observed |

**The inventory is tiny on purpose.** Anthropic's motion language is "hard cut + occasional scale pop + typewriter." That's it. Anything more is off-brand.

---

## 6. Audio

Neither video has voiceover. Both use instrumental music only.

- V1 (Opus 4.6): upbeat, cinematic-tech score with a rising synth motif. Every hard cut lands on a beat. Music is the narrative — no SFX, no stings.
- V2 (Chrome): gentle, ambient, almost lo-fi piano/pad. Much lower energy. Music reinforces the "calm competence" pacing.

**Silence as a tool**: Both films end on 2-5 seconds of near-silence while the wordmark holds. That silence is the mic-drop.

---

## 7. Branding — When/Where the Logo Appears

- **Never during the main body** of either film. The Claude Spark icon does not appear as a watermark, corner logo, or chyron.
- **Only on the final card**. V1: `Opus 4.6 by ANTHROP\C` (wordmark logo). V2: `[Spark icon] Claude` + `Visit claude.com/chrome` (brand lockup + URL).
- The mascot from your `claude_mascot_anthropic_brand_kit.svg` does NOT appear in these two films. Anthropic reserves the mascot for product UI and docs, not cinematic release videos.
- A tiny Claude Code "bug" / pixel-art avatar DOES appear inside the Claude Code terminal frame in V2. It's in-situ product chrome, not cinematic branding.

---

## 8. Camera Moves

**None.** Every frame is a static plate. No pans, no zooms, no parallax, no kenburns. Motion happens inside the mockups (scrolling docs, opening tabs, typing text); the camera never moves.

This is a strong constraint to respect in Remotion: your Compositions should be fixed-viewport. Motion is applied to *elements within* the frame, not to the frame itself.

---

## 9. Information Density

- **Opus 4.6 montage frames**: high density — 4-6 UI mockups tiled at once, each with its own tweet overlay. Reads as "there is cultural noise about Claude and it's everywhere."
- **Opus 4.6 wordmark frames**: extreme low density — two words of text on an otherwise empty cream plane.
- **Chrome demo frames**: medium density — one browser window + one Claude sidebar, each with real product UI. Reads as "this is what one focused person does with Claude."
- **Chrome callout frames**: extreme low density — one line of serif-display headline on sand. Period.

**The rhythm is density → density → [MIC DROP LOW DENSITY CARD] → density → density → [LOW DENSITY CARD].** High-to-low is the beat structure. Your Remotion composition should do the same: busy HUD shots then drop to a single centered phrase.

---

## 5-7 Concrete Remotion Principles (apply directly to `demo-presentation/`)

1. **Background = `#E0D8C8` sandstone for any "product demo" shot; `#F8F8F8` cream for any "wordmark / model" shot.** Never pure white, never gray. One swap in Remotion defines the whole film's class.

2. **One accent color, period. `#D97757`.** Use it only on: send/ship/submit buttons, the Claude Spark icon, slide-comment chips, italic emphasis inside headlines. The tennis biometric HUD's SignalBar can use this coral as its "live / attention-worthy" color — but nothing else on screen gets coral.

3. **Typography pair: Copernicus (or free alt: Fraunces / Playfair Display) for hero headlines + numbers; Styrene-analog (or free alt: Inter / Geist) for UI and captions.** Set your Remotion `<Composition>` default to the serif for big moments, fall back to sans for captions + HUD chrome. Italic for emphasis inside a serif headline is on-brand.

4. **Pacing contract for the demo video**: open with a Chrome-film-style calm beat (8-9s dwell) on "here's what Panopticon sees — one player, one court," then in the signal-extraction montage shift to Opus-4.6-film pacing (~1 cut/sec) while music ramps, then drop back to long-dwell (~6s) for the Opus Coach chat-panel reveal, then END on 4 seconds of held cream with the wordmark `Panopticon Live by [your name]` in Copernicus on #F8F8F8. Inversion of tempo is the punctuation.

5. **Motion primitives list (close the menu to only these)**: (a) hard cut, (b) scale-pop-in at ~0.9 → 1.0 over 250ms with slight overshoot spring, (c) typewriter word-reveal at 60-80ms/char inside Claude-styled chat panels, (d) ONE crossfade, reserved for the montage-to-wordmark transition. Do not add whooshes, glows, blur reveals, or camera drifts. Respecting this constraint is how you *read* as Anthropic-native.

6. **Framing rule**: every composition is static-camera. Motion happens only inside mockups — HUD stats ticking up, court overlays highlighting, Opus chat messages appearing. Never pan or zoom the camera itself. In Remotion this means no `translateX` on the root Composition; only on children.

7. **Sound contract**: no narration, music-only. Land cuts on downbeats. Build to 2-5 seconds of silence at the end before the wordmark fade-up. This is the single biggest craft lever and costs $0 — just pick an instrumental track from Musicbed / Artlist in the 90-120 BPM range with a clear downbeat structure.

---

## Appendix A — Scene-by-Scene Logs

### V1 (Opus 4.6, 39s) — sampled at 1.5s intervals
- 00:00-00:03 — newspaper front-page closeup, serif headline `Claude Is Ta... Storm, and...` (cultural proof: print media)
- 00:03-00:05 — sans "model, Claude" typography macro shot (Anthropic's own marketing)
- 00:05-00:08 — chalkboard covered in handwritten math equations, Instagram overlay `ohnohanajo: Math just made a little more sense. Thanks Claude.` (proof: academia)
- 00:08-00:10 — woman walking with tweet overlay (proof: daily life)
- 00:10-00:13 — woman holding hand-knit sheep-sweater, tweet `(Abi)gail: Most people: I use Claude to vibe code.` (proof: coders + hobbyists)
- 00:13-00:16 — brain MRI scan with tweet `tobi lutke` (proof: tech CEOs)
- 00:16-00:19 — water pipes / HVAC install with tweet `Ben Pouladian: Just used Claude Cowork to...` (proof: blue-collar professionals)
- 00:19-00:22 — dense screen-collage grid (proof: scale)
- 00:22-00:25 — Mars rover footage (proof: science/NASA)
- 00:25-00:28 — `Opus 4.5` wordmark on cream, scale-warp transition
- 00:28-00:30 — `Introducing / Opus 4.6` wordmark with collage bleed on right
- 00:30-00:33 — `Opus 4.6 is remarkably capable.` — note the period, the understatement
- 00:33-00:36 — multi-product carousel (drum machine, slide deck, style guide, typography generator)
- 00:36-00:39 — `Opus 4.6 by ANTHROP\C` final card, held

### V2 (Claude for Chrome, 95s) — sampled at 3s intervals
- 00:00-00:05 — hand-drawn sketch of a window with a cursor on sand bg (literal preview of what's coming)
- 00:05-00:10 — `Pull context from anywhere` serif headline on sand (section title)
- 00:10-00:20 — empty Google Doc in Chrome window on sand, cream-gloved cursor hovers
- 00:20-00:30 — 4 dashboard tabs open (revenue, Patronly, Beaconify, Glintmetric), cursor moving between them
- 00:30-00:45 — Claude sidebar slides in from right, prompt types out word-by-word, Weekly Business Snapshot doc fills in
- 00:45-00:55 — `Address slide comments automatically` headline → Google Slides with multiple coral comment chips from Sarah/Nicole/Drew
- 00:55-01:10 — slides get edited, comments resolved, the `$15M` revenue slide renders with coral "Sarah" comment fading out as complete
- 01:10-01:25 — section title → Claude Code terminal on sand bg, `> update our homepage to match this design`, agent starts "Hatching..." (note the sparkle/coral accent on status)
- 01:25-01:35 — Chrome switches to localhost:8000, new homepage renders with italic "actually" in the serif headline
- 01:35-01:35 — `[Spark] Claude` + `Visit claude.com/chrome` final card, held

---

## Appendix B — What We Still Don't Know

- Music licensing — Anthropic doesn't list the track. Use a BPM-matched instrumental from Artlist.
- The EXACT font files — I'm inferring from visual match. Safe free substitutes: **Fraunces** (serif), **Inter** or **Geist** (sans). Paid equivalents to match more precisely: **Copernicus** (Commercial Type), **Styrene B** (Commercial Type).
- Whether the cursor in V2 is a real macOS cursor or a custom-drawn asset (it has a slightly coral tint at the tip, so likely custom-composited in After Effects / Remotion).
- Whether the tweet overlays in V1 are real tweets (the handles look plausible; `@tobi` is Tobi Lütke, so at least some are real).

---

## File Locations

- This cheatsheet: `/Users/andrew/Documents/Coding/hackathon-research/demo-presentation/assets/references/anthropic_video_dna.md`
- Source videos: `/tmp/anthropic_dPn3GBI8lII.webm`, `/tmp/anthropic_rBJnWMD0Pho.webm`
- Frame samples V1 (26): `/tmp/anthropic_frames_v1/f_001.png` … `f_026.png`
- Frame samples V2 (32): `/tmp/anthropic_frames_v2/f_001.png` … `f_032.png`
- Info JSON: `/tmp/anthropic_dPn3GBI8lII.info.json`, `/tmp/anthropic_rBJnWMD0Pho.info.json`
- Official brand-kit SVGs already in this folder: `claude_logo_slate_OFFICIAL.svg`, `claude_spark_clay_OFFICIAL.svg`, `claude_icon_rounded_OFFICIAL.svg`, `claude_code_logo_slate_OFFICIAL.svg`, `claude_mascot_anthropic_brand_kit.svg`
