# Even G2 — Capability Map (researched, evidence-based)

**Status:** Sprint 6 discovery · facts for design, not assumptions. **Method:** public sources
(Even Realities official pages + independent coverage), 2026-06. Each capability is tagged
**Confirmed** (stated by the vendor or corroborated across sources), **Likely** (reasonable
inference, not directly stated), or **Unknown** (not found / must be verified with Even
Realities). Where a claim drove a design decision, the implication is noted. **Do not build
against anything tagged Unknown without confirming it.**

## 1. Confirmed

| Capability | Detail | Source |
| --- | --- | --- |
| **Display: monocular green HUD** | A single-eye green **monochrome** micro-LED + waveguide (HAO 2.0); fronts/temples magnesium+titanium | techeblog; evenrealities |
| **Field of view 27.5°, 60 Hz** | Small heads-up canvas, one eye | techeblog |
| **Brightness up to 1200 nits** | **Bright enough to read in sunlight** — important for a greenhouse | techeblog |
| **No camera — by design** | "Camera-free. By design. No recording and social friction." | evenrealities (×2) |
| **No speakers** | "no speakers, so talks remain private" — **display-only; no audio output** | techeblog |
| **4 microphones + "Hey Even" voice** | Voice **input**; assistant remembers prior questions (context) | evenrealities; techeblog |
| **Input: voice + temple touch + Even R1 ring** | "finger taps on the arm modules"; R1 ring "tap, slide, or press" | techeblog; evenrealities |
| **Geomagnetic sensor** | Compass — drives a navigation overlay | techeblog |
| **Phone companion app, Bluetooth 5.2** | Setup/relay via the Even Realities app | evenrealities |
| **~36 g, IP65, ~2-day battery + case (≈7 charges)** | Lightweight; dust-tight, water-resistant; all-day wear | evenrealities; techeblog |
| **Built-in functions: notifications, Translate, Conversate, "Ambient AI Prompts"** | Vendor surfaces text prompts to the HUD today | evenrealities |
| **"Even Hub" developer portal exists** | A developer/community portal is referenced; apps "coming" | evenrealities |

## 2. Likely (not directly confirmed)

| Capability | Why likely | Risk if wrong |
| --- | --- | --- |
| **IMU / accelerometer** | A geomagnetic sensor is confirmed; motion sensing usually accompanies it (head/step detection) | If absent, no on-glasses motion/step cues; rely on phone |
| **Notification relay from arbitrary phone apps** | G1 did this; G2 markets notifications | If restricted, Gaia text must use a sanctioned channel |
| **Ambient-light/auto-brightness** | 1200-nit display in variable light usually auto-dims | Minor; manual brightness otherwise |
| **Prescription-lens integration** | Even Realities' core differentiator | None for Gaia |

## 3. Unknown — must be verified with Even Realities before depending on it

| Question | Why it matters to Gaia | How to resolve |
| --- | --- | --- |
| **Is there an open SDK/API, and what can a 3rd party render to the HUD?** | This is the single gating dependency for any real Even G2 Companion — can Gaia push its own one-line messages and read voice/ring input? | Even Hub developer portal / Even Realities developer relations |
| **Exact text capacity per screen** (lines × characters at 27.5°) | Sets the real one-screen budget (the Field Companion assumed ≤~40 chars / one line) | Device testing |
| **Can it render simple glyphs/icons, or text only?** | Affects whether status/urgency can be glanceable symbols | Device testing |
| **Latency of voice intent + ring events to a 3rd-party app** | Field interactions must feel instant | Device testing |
| **Offline behavior** (does the HUD work without phone/network?) | Greenhouses have flaky connectivity (Sprint 5 §7) | Device testing |
| **Multi-user / shared-device provisioning** | Multiple growers, shifts | Even Realities |

## 4. Design implications (what the evidence forces)

1. **The glasses are output + voice-in, not a sensor of plants.** No camera means **Even G2
   never observes the crop**; in Observer-Network terms it is *a device of the human Observer*
   (their eyes/voice), not an Observer itself. Imaging observations must come from the **phone
   camera, fixed cameras, or a drone**. (This is exactly what `specs/observer-network.md` §2
   already states — the research confirms it.)
2. **Output is silent visual text only.** No speakers means Gaia **cannot talk**; it shows a
   short line on a one-eye green HUD. This *strengthens* the calm philosophy: one thought, a
   glance, default to silence — there is literally no way to be noisy. Voice is the grower's
   way *in*, not Gaia's way *out*.
3. **Tiny monocular canvas + sunlight-bright** validates the Field Companion's small-display
   rules (one message, ≤ one short line, no scrolling/menus/typing). 1200 nits means it is
   usable in the greenhouse glare.
4. **Input is voice + ring/temple gestures** — confirms "no typing." Answers are a **tiny fixed
   set** chosen by ring scroll/tap or a short spoken word (the Field Companion's option model
   maps directly to R1 gestures).
5. **SDK is the one true unknown.** Until Even Realities confirms what a third party may render
   and read, the live-device transport (the Field Companion's `EvenG2Display._send_to_device`)
   stays a stub. Treat SDK access as a **hard dependency and risk** in the roadmap.

## 5. Sources

- [Even Realities — Smart Glasses (official)](https://www.evenrealities.com/smart-glasses)
- [Even Realities — Buy Even G2 A (official)](https://www.evenrealities.com/products/g2-a)
- [TechEBlog — Even Realities G2 specs/price/release](https://www.techeblog.com/even-realities-g2-smartglasses-specs-price-release-date/)
- [EuroOptica — Even Realities G2](https://www.eurooptica.com/pages/even-realities-g2)
- [Celmin — Even Realities G2 Explained](https://celmin.ca/even-realities-g2-explained/)
- Even Support Center — Specs page exists but returned HTTP 403 to automated fetch; verify manually: `support.evenrealities.com` → Specs.
