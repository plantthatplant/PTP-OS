# Gaia on Even G2 — build & deploy log

The real Gaia app for the Even G2 glasses. On launch the HUD shows, in order:

1. `Gaia is connected.`
2. `Good morning, Oskar.`
3. the real **Morning Brief** from the Gaia API (`GET /api/v1/morning`).

Then you can **talk to Gaia** (see below). It holds no intelligence — it renders what the Gaia
API decides, and says so honestly if the API is unreachable (it never invents an answer).

---

## Talk to Gaia (voice)

**Gestures on the HUD:** single **tap** = start listening → **tap** again = ask · **double‑tap** = exit.

Flow: tap → `Listening…` (mic opens via `audioControl`) → speak → tap → `Thinking…` → Gaia's
answer. The glasses capture PCM and `POST` it to `/api/v1/ask`; the **Gaia server** does
speech‑to‑text (OpenAI Whisper) **and** reasoning (Claude, grounded in the live greenhouse),
then returns text. **The G2 has no speaker — Gaia replies as text.**

Keys live **only on the Gaia server** (never on the glasses). Start the API with both:

```bash
cd ~/Documents/GitHub/PTP-OS && git checkout feat/gaia-voice-ask
pkill -f api.server
OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-ant-... GAIA_API_KEY=gaia-dev-key python3 -m api.server
# optional, snappier on-HUD latency:  GAIA_ANSWER_MODEL=claude-sonnet-4-6
```

Until both keys are set, `/api/v1/ask` returns an honest line (e.g. *"Gaia's reasoning is not
configured"*) — never a crash, never a fabricated answer. Each question costs Whisper + Claude.
The `g2-microphone` permission is declared in `app.json`.

---

## What was verified before any code (SDK capability check)

Against the SDK type defs (`@evenrealities/even_hub_sdk` v0.0.11), the official templates, and an
independent feature-verification writeup:

| Capability | Verdict |
|---|---|
| Custom UI rendering | ✅ via Text/Image/List containers, 576×288 4‑bit greyscale |
| Networking HTTP/HTTPS | ✅ standard WebView `fetch` (not an SDK method); CORS/TLS apply |
| Authentication | ⚠️ identity only (`getUserInfo`/`getDeviceInfo`) + storage; no auth framework |
| Local storage | ✅ `setLocalStorage`/`getLocalStorage` (string K/V) |
| Voice events | ✅ mic + PCM via `audioControl` + `audioEvent`; ❌ no built-in STT |
| Ring events | ✅ R1 ring + temple touch as `CLICK`/`DOUBLE_CLICK`/`SCROLL` events |
| Notifications | ❌ no outbound/background push to the glasses (only inbound events) |

Only **notifications** is a true gap, and it is **not** on the critical path for this app
(Gaia is a foreground, glanceable, polling app — not a background pusher).

## Toolchain installed

- Node.js 26.4.0 + npm 11.17.0 (via Homebrew — was not previously installed).
- Project deps: `@evenrealities/even_hub_sdk@0.0.11`, `@evenrealities/evenhub-cli`, Vite 5, TypeScript 5.

## Project layout (`~/Documents/gaia-even`)

```
app.json            Even Hub manifest (package_id com.plantthatplant.gaia)
index.html          phone-side page (the real UI is on the glasses)
vite.config.ts      dev server + /gaia proxy → Gaia API (same-origin, no CORS needed)
src/main.ts         the 3-stage flow + Morning Brief fetch
src/vite-env.d.ts   import.meta.env typing
```

## How the glasses reach Gaia (the key design point)

The glasses run this app inside the Even Hub companion app's WebView, loaded over the LAN from
the Vite dev server. To avoid CORS / mixed-content, the app calls a **same-origin path**
(`/gaia/...`) and **Vite proxies it server-side** to the real Gaia API. So the phone only talks
to the dev server; the dev server talks to Gaia on `127.0.0.1:8000`.

## Run it (two servers)

```bash
# 1) Gaia API (from the PTP-OS repo)
cd ~/Documents/GitHub/PTP-OS
GAIA_API_KEY=gaia-dev-key python3 -m api.server          # → 127.0.0.1:8000

# 2) the Even app dev server
cd ~/Documents/gaia-even
npm run dev                                              # → 0.0.0.0:5173 (LAN: 192.168.1.3)
```

### Verified end-to-end (all green)
- `GET http://127.0.0.1:8000/api/v1/morning` → real brief (Kalaberga, confidence Medium)
- `GET http://192.168.1.3:5173/` → 200 (app served on the LAN)
- `GET http://192.168.1.3:5173/gaia/api/v1/morning` → 200 (proxy → Gaia)

## Load onto the real glasses (developer QR flow)

```bash
cd ~/Documents/gaia-even
npx evenhub qr --url http://192.168.1.3:5173          # printed + -e opens it on screen
```

1. Make sure the **phone is on the same Wi-Fi** as this Mac (`192.168.1.3`).
2. Open the **Even Hub companion app** (phone paired with the G2).
3. **Scan the QR.** The app loads on the glasses.
4. **Wear the glasses** → watch the three stages appear.
   - Single tap = refresh the brief · Double-tap = exit.

## Permanent install (distributable package)

```bash
cd ~/Documents/gaia-even
npm run build                                           # → dist/
npx evenhub pack app.json dist                          # → out.ehpk  (33 KB, built)
# then: npx evenhub login  → upload out.ehpk via the Even Hub dev portal → install OTA
```

## Notes / limits

- **Reachability:** the QR URL and the proxy target use `192.168.1.3`. If the Mac's LAN IP
  changes, regenerate the QR and restart `npm run dev`.
- **For a hosted (non-LAN) deployment**, the Gaia API needs a public HTTPS URL + per-client key,
  and the app would call it directly (`VITE_GAIA_API_URL`) — at which point the API's CORS
  support (the open PR) is required. The dev/QR flow above does not need it (same-origin proxy).
- **Brief content** comes straight from `GET /api/v1/morning`; the app does no reasoning.
