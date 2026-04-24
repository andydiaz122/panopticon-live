# Anthropic Brand & Claude Mascot Usage Research

**Date**: 2026-04-24
**Project**: Panopticon Live (Built with Opus 4.7 hackathon, due 2026-04-26 8pm EST)
**Question**: Can we use the Claude mascot in our demo video opener?
**Bias**: Caution — disqualification risk dominates aesthetic upside.

---

## TL;DR — VERDICT: **RISKY (lean FORBIDDEN)** for the canonical "Clawd" mascot. **CONDITIONAL-SAFE** for the official Claude logo/icon/Spark from the press kit, used minimally as attribution.

**Recommendation**: Do **NOT** use the "Clawd" pixel-crab mascot. Use the **official "Claude icon" (rounded square, orange gradient + white Spark)** from Anthropic's press kit ONCE, as a small attribution chip in a "Built with Opus 4.7" lockup at the very end of the video — and build a Remotion-native facsimile (rounded square + Spark glyph + small "thinking" pulse) for the opener if we want a "mascot-like" personality.

---

## 1. MASCOT SVG SOURCE — what is and isn't downloadable

### Official Anthropic press kit (downloaded 2026-04-24)

**Source**: https://anthropic.com/press-kit (redirects to a CDN ZIP — `https://www-cdn.anthropic.com/ae59ca4ca194dac9c9dc3bc78c5829468cb0e8af.zip`, ~26 MB).

**Contents (logos only — NO mascot character):**

| Asset | Variants | What it is |
|---|---|---|
| Anthropic logo (wordmark) | Slate, Ivory | "anthropic" lowercase wordmark |
| Anthropic symbol | Slate, Ivory | The Anthropic abstract mark |
| **Claude logo** | Slate, Ivory, One-color | "Claude" wordmark + Spark |
| **Claude Code logo** | Slate, Ivory, One-color | "Claude Code" wordmark + Spark |
| **Claude Spark — Clay** | SVG, PNG | The orange asterisk-star (`#D97757`) — the closest thing to a "mark" or "mascot" |
| **Claude icon** | Rounded (gradient bg), Square (gradient bg) | App-icon style: orange gradient + white Spark on rounded/square |
| Leadership headshots | JPGs | Dario, Daniela, Jack Clark, Jared Kaplan |

**Critically missing from the press kit**: any pixel-art "Clawd" character, any humanoid mascot, any animated mascot, any walking/head-tilting animation cells. **The "Clawd" pixel crab is NOT in the press kit.** It exists only on Claude Code's social media (an Instagram Reel introducing Artifacts, an X post in Sept 2025) and is documented to be "completely absent from the product itself and any accompanying documentation" (GitHub issue #8536). When users asked Anthropic on GitHub why Clawd's color changed from orange to blue (issue #13755), the issue was closed as "not planned" with no official response — confirming Clawd is semi-official at best, and definitely not a sanctioned brand asset for third-party use.

### Files saved to `/Users/andrew/Documents/Coding/hackathon-research/demo-presentation/assets/references/`

- `claude_spark_clay_OFFICIAL.svg` — The orange Spark (`#D97757`) — the abstract asterisk-star mark
- `claude_logo_slate_OFFICIAL.svg` — "Claude" wordmark + Spark in slate (`#141413`)
- `claude_icon_rounded_OFFICIAL.svg` — Rounded square, orange gradient (`#DC6038`→`#D97757`) + white Spark
- `claude_code_logo_slate_OFFICIAL.svg` — "Claude Code" wordmark + Spark in slate
- `claude_mascot_anthropic_brand_kit.svg` — Wikimedia Commons CC0 version of the Spark (1200×1200, large viewBox); essentially the same shape as `claude_spark_clay_OFFICIAL.svg` but at higher resolution. **Note: the filename is misleading — this is the Spark, not a mascot. CC0 covers copyright but NOT trademark; do NOT rely on Wikimedia's CC0 dedication to override Anthropic's trademark rights.**

---

## 2. LICENSING VERDICT

### Anthropic's Consumer Terms of Service (verbatim)

> "You may not, without our prior written permission, use our name, logos, or other trademarks in connection with products or services other than the Services, or in any other way that implies our affiliation, endorsement, or sponsorship."
>
> Permission requests: **marketing@anthropic.com**

Source: https://www.anthropic.com/legal/consumer-terms (Privacy/Trademark section)

### Anthropic's Commercial Terms (Section G — Publicity)

> "Anthropic reserves the right to use Customer's name and logo to publicly identify Customer as a customer of the Services" — i.e., the right flows ONE WAY (Anthropic → about us, not us → about Anthropic).

Source: https://www.anthropic.com/legal/commercial-terms

### Cerebral Valley hackathon rules

The "Built with Opus 4.7" hackathon page (https://cerebralvalley.ai/e/built-with-4-7-hackathon) requires participants to "accept the intellectual property conditions and code of conduct before receiving Claude Code access credentials." Confirmed via search results: **"participants retain all rights to their creations and no licensing obligation to Anthropic or Cerebral Valley"** — which protects OUR IP, but does NOT grant us reciprocal rights to use Anthropic's branding. The hackathon rules do not waive Anthropic's standard ToS trademark restriction.

### What this means concretely

| Action | Verdict | Why |
|---|---|---|
| Use the "Clawd" pixel-crab mascot in our demo | **FORBIDDEN** | Not in the official press kit. Semi-official at best. Using it implies endorsement, which the ToS explicitly prohibits. Risk: looks unprofessional + invites a takedown / disqualification challenge. |
| Use the official Claude logo / Spark / icon throughout the demo | **RISKY** | The press kit makes the assets DOWNLOADABLE, but the ToS still requires written permission for any use that "implies affiliation, endorsement, or sponsorship." Heavy use throughout a demo could read as "endorsed by Anthropic." |
| Use the official Claude logo / Spark / icon ONCE as a small attribution chip ("Built with Opus 4.7" lockup) at the end of the demo | **CONDITIONAL-SAFE** | This is descriptive use ("we built this with their tool"), which is the same posture the press kit was designed for and parallels the existing "Powered by Claude" partner ecosystem. Still technically requires written permission per the strict ToS reading, but is the lowest-risk usage that judges will not flag. |
| Build a Remotion-native facsimile (rounded square + Spark-shaped glyph + animation) that EVOKES the icon without reproducing it | **SAFEST** | Trademark-clear if it's geometrically distinct. Use Anthropic's brand colors (`#D97757` orange, `#141413` slate, `#FAF9F5` ivory) since colors are not trademarkable, and the `anthropics/skills` brand-guidelines repo publishes them under Apache 2.0. |

### CC0 trap on the Wikimedia Spark SVG

The Wikimedia Commons file (https://commons.wikimedia.org/wiki/File:Claude_AI_symbol.svg) is dedicated CC0. **CC0 waives copyright; it does NOT waive trademark.** Anthropic still owns "Claude" and the Spark glyph as trademarks. Downloading the SVG from Wikimedia does not give us license to use it in a way that implies affiliation. Treat the Wikimedia file as a high-resolution reference — same legal posture as the press-kit version.

---

## 3. PRIOR-ART REFERENCE — did Built with Opus 4.6 winners use the mascot?

**Findings**: The Built with Opus 4.6 hackathon (Feb 2026) had ~13,000 applicants, 500 builders, and 5 named winners. Their demo video URLs:

- 1st place — CrossBeam: https://www.youtube.com/watch?v=jHwBkFSvyk0
- 2nd place — Elisa: https://www.youtube.com/watch?v=rsUaz_QAK6o
- 3rd place — PostVisit.ai: https://youtu.be/V29UCOii2jE
- Keep Thinking Prize — TARA: https://www.youtube.com/watch?v=GFCrXehS1DE
- Creative Exploration Prize — Conductr: https://www.youtube.com/watch?v=X6CqJoyj0kI

I could not extract video frames via WebFetch (YouTube returns only navigation chrome). The Anthropic blog post praising the winners (https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon) describes what each project DOES (CrossBeam generates permit plans in 20 minutes; TARA produces assessment reports in 5 hours), but conspicuously does NOT call out any winner using the Claude mascot or branding in their demo. **No 4.6 winner is publicly documented as using a Claude mascot in their video.** This is a non-trivial signal: if mascot use were a winning strategy, Anthropic's recap blog would have name-checked it.

**Limitation**: I could not retrieve the actual video frames. If you want certainty here, manually scrub the first 10 seconds of each demo above and check for orange Sparks / mascots / logos. My priors based on the absence of mascot mentions in Anthropic's own blog: **assume no winner used the mascot**, and act accordingly.

---

## 4. CANONICAL MASCOT BEHAVIOR (in Anthropic's own content)

The "Clawd" character — to the extent it has canonical behavior — appears in two places:

1. **The Instagram Reel introducing Artifacts** (https://www.instagram.com/reel/C8cUns1uQ4H/) — captioned "Claude, meet...Claw'd. We've just launched a preview of Artifacts on claude.ai." The reel emphasizes the FEATURE (Artifacts) not the mascot; Clawd appears as a brief character introduction. Design: 8-bit pixel-art crab/sprite.
2. **The Claude Code terminal welcome screen** (per GitHub issue #8536 and https://www.starkinsider.com/2025/10/clawd-ai-retro-mascot-command-line.html) — when you run `# claude` in the terminal, an 8-bit pixel sprite "pops up at the top of any new coding session." It is described as static — "no measurable productivity gain. No fancy animation. Just a tiny pixel pal staring back at you." Color was originally orange; changed to blue in Claude Code v2.0.67 (per issue #13755); change was undocumented and the issue was closed as "not planned."

There are also community projects that animate Clawd (e.g., `claude-code-mascot-statusline`, `clawd-on-desk`) — these are **explicitly unaffiliated fan projects**, not endorsed by Anthropic, and carry no usable license for our purposes.

### The Spark itself — how it animates in Anthropic's official content

The orange Spark (Claude logo) appears in Anthropic's official keynotes and product launch videos with a few canonical motions:
1. **Subtle pulse / breathing scale** during "thinking" or model reasoning shots
2. **Rotation around its center** when used as a loading indicator
3. **Stroke draw-on** (drawing the asterisk path from one stroke to all six) for intro reveals
4. **Gentle parallax / float** on landing pages

These behaviors are not exclusive to Anthropic's IP — pulse, rotate, draw-on, and float are generic motion-design vocabulary. **A facsimile that pulses and rotates is geometrically separate from the Spark and trademark-safe.**

---

## 5. SAFE-USAGE PATTERN — concrete recommendation

### What we should NOT do

- **No "Clawd" pixel crab.** Not in the press kit. Closing of issue #13755 with no official response indicates Anthropic is deliberately keeping Clawd in a semi-official limbo. Using a non-sanctioned, undocumented mascot in a video that will be evaluated by Anthropic judges is the highest-variance, lowest-upside choice on the board.
- **No Spark / Claude logo as a recurring character throughout the demo.** Heavy use reads as "endorsed by Anthropic," which the ToS prohibits without written permission.
- **No "Anthropic" wordmark anywhere prominent.** Same reason. Per Section G of the Commercial Terms, the publicity right flows Anthropic → us, never the reverse.

### What we SHOULD do

**Option A — Conservative (recommended for hackathon submission):**
1. Build a **Remotion-native facsimile** for any "mascot-like" personality in the opener. A rounded square (`128×128, rx=30`, gradient `#DC6038`→`#D97757`) with a **geometrically-distinct glyph** inside (NOT the Spark — e.g., a stylized tennis-ball circle, a custom geometric mark, or your project's own logo) + a subtle pulse-and-float animation. Use Anthropic's published color palette (`#141413`, `#FAF9F5`, `#D97757`) — colors are not trademarkable.
2. End the video with a single, small, attribution-chip lockup: `[official Claude icon, ~48px] Built with Claude Opus 4.7` in the lower-right corner of the closing frame, displayed for ≤3 seconds. Use `claude_icon_rounded_OFFICIAL.svg` from the press kit — at small size, in attribution context, with descriptive language ("Built with"). This parallels Anthropic's own "Powered by Claude" partner program and is the lowest-risk official-asset use possible.
3. Do NOT add a verbal "Thanks Anthropic" or "Anthropic-endorsed" callout in narration. Keep it descriptive: "Built with Claude Opus 4.7."

**Option B — If you want to go slightly bolder (only if you also email marketing@anthropic.com today):**
- Email `marketing@anthropic.com` THIS AFTERNOON with a 3-line ask: "Hi — I'm a Built with Opus 4.7 hackathon participant. I'd like to display the official Claude icon and 'Built with Opus 4.7' lockup in my 3-minute demo video closing frame. Permission?" Even if they don't respond by Sunday, you'll have a documented good-faith request, which materially de-risks the situation.

**Option C — Maximum safety (recommended if you have any remaining doubt):**
- Use ZERO Anthropic visual assets in the video. Mention "Claude Opus 4.7" verbally and as text-only in a closing card ("Built with Claude Opus 4.7 — claude.com"). Words and product names used descriptively (i.e., to identify what tool you used, not to imply endorsement) are nominative fair use under U.S. trademark law and well-established in software credits.

### Concrete attribution lockup spec for Option A

```
[bottom-right corner of final frame, displayed 3.0s]

  ┌──────────────────────────────────────────┐
  │                                          │
  │        [Claude icon, 48×48px]            │
  │        Built with Claude Opus 4.7        │
  │                                          │
  └──────────────────────────────────────────┘

  Padding:    24px
  Font:       Poppins 16pt (matches Anthropic brand guidelines)
  Color:      slate #141413 on ivory #faf9f5 OR ivory on slate
  Icon file:  claude_icon_rounded_OFFICIAL.svg (from press kit)
```

---

## Sources

- Anthropic Consumer Terms of Service: https://www.anthropic.com/legal/consumer-terms (trademark restriction quoted verbatim above)
- Anthropic Commercial Terms of Service: https://www.anthropic.com/legal/commercial-terms (Section G — Publicity)
- Anthropic Press Kit (official, downloaded 2026-04-24): https://anthropic.com/press-kit
- Anthropic brand-guidelines skill (Apache 2.0): https://github.com/anthropics/skills/tree/main/skills/brand-guidelines
- Cerebral Valley hackathon page: https://cerebralvalley.ai/e/built-with-4-7-hackathon
- Built with Opus 4.6 hackathon winners (recap): https://claude.com/blog/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon
- Clawd mascot status (semi-official, not in press kit): https://github.com/anthropics/claude-code/issues/8536
- Clawd color-change issue closed as "not planned": https://github.com/anthropics/claude-code/issues/13755
- Wikimedia Commons Claude AI symbol (CC0 — copyright only, NOT trademark): https://commons.wikimedia.org/wiki/File:Claude_AI_symbol.svg
- "Powered by Claude" partner showcase (parallel to attribution chip use): https://claude.com/partners/powered-by-claude

---

## Caveats / what I could NOT verify

1. **I did not visually inspect the 5 winner demos from Built with Opus 4.6.** WebFetch on YouTube returns only chrome. If you want certainty, scrub the first 10s of each video manually. My prior: zero of them used the mascot.
2. **I did not attempt `marketing@anthropic.com`.** The ToS-compliant path is to email them; the practical path for a hackathon due in 60 hours is Option A (facsimile + small attribution chip) and ship.
3. **I did not find an explicit "hackathon participant" carve-out in any Anthropic policy.** None exists publicly. The Cerebral Valley hackathon's IP clause protects OUR work, not OUR right to use Anthropic's marks.
