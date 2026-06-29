# Gaia on Even G2

The production Even Hub app that puts Gaia on the Even G2 smart glasses. It is a **thin window**:
it renders what the Gaia API decides and captures the grower's voice — it holds **no greenhouse
intelligence** (ADR-005/006). All reasoning lives behind the Gaia API.

On the HUD:

1. `Gaia is connected.` → `Good morning, Oskar.` → the real **Morning Brief** (`GET /api/v1/morning`).
2. **Talk to Gaia:** single **tap** = start listening → **tap** = ask · **double-tap** = exit.
   The glasses capture mic PCM and `POST` it to `/api/v1/ask`; the server does speech-to-text and
   reasoning and returns text. *The G2 has no speaker — Gaia answers as text.*

Honest by construction: if the API is unreachable or a key is missing, it shows a plain message —
never an invented brief or answer.

## Stack

Vite + TypeScript + [`@evenrealities/even_hub_sdk`](https://www.npmjs.com/package/@evenrealities/even_hub_sdk)
(pinned to `0.0.11`). Requires Node 18+.

```
app.json            Even Hub manifest (package_id, g2-microphone permission)
index.html          phone-side page (the experience is on the glasses)
vite.config.ts      dev server + /gaia proxy → Gaia API (same-origin in dev, no CORS needed)
src/main.ts         the brief sequence + voice loop (the whole app)
```

## Run against a local Gaia API

```bash
# 1. Gaia API (from the repo root)
GAIA_API_KEY=gaia-dev-key python3 -m api.server          # → 127.0.0.1:8000
#    for voice, also set:  OPENAI_API_KEY=…  ANTHROPIC_API_KEY=…  (server-side only)

# 2. this app
cd companion/even-hub-gaia
npm install
npm run dev                                              # → 0.0.0.0:5173

# 3. load onto the glasses (phone on the same Wi-Fi, Even Realities app, Hub tab → scan)
npx evenhub qr --url http://<your-lan-ip>:5173
```

The glasses' WebView calls a **same-origin** path (`/gaia/...`) that Vite proxies to the Gaia API,
so dev needs no CORS and no LAN IP in the app. For a packed/hosted build, set `VITE_GAIA_API_URL`
to the hosted API (which then needs TLS + the CORS support already in `api/server.py`).

## Package for distribution

```bash
npm run build && npx evenhub pack app.json dist          # → an .ehpk to upload via the Even Hub portal
```

## Config

`.env.example` → copy to `.env.local`:

| Var | Default | Meaning |
|---|---|---|
| `VITE_GAIA_API_URL` | `/gaia` (dev proxy) | Gaia API base; set to the hosted URL for a packed build |
| `VITE_GAIA_API_KEY` | `gaia-dev-key` | sent as `Authorization: Bearer` to the Gaia API |

The OpenAI/Anthropic keys that power voice live **only on the Gaia server**, never here.

See [`DEPLOY.md`](DEPLOY.md) for the full build/deploy log, the SDK capability verification, and
the on-glasses test steps.
