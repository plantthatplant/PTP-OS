# Gaia on Even G2 — Even Hub plugin

One line of a head grower's judgement, when it matters, and silence the rest of the day.

This is the **window** the product review called "the film": Gaia on the glasses. It is not Gaia —
it holds no intelligence (ADR-005/006). It fetches Gaia's *one thought* from the
[Gaia API](../../docs/gaia-api.md) `GET /api/v1/companion` and renders a single line on the G2 HUD.
On the phone it is the Even-side embodiment of the Companion bridge (ADR-008): the glasses never
talk to Gaia; this plugin (running in the Even app) does.

> Grounded in Even Realities' official SDK and `evenhub-templates` (the `minimal` + `asr` scaffolds).
> Verify against the current SDK at https://hub.evenrealities.com/docs before shipping.

## The experience (The One Thought Principle)

- **It shows judgement, never data.** Not "House 2 · 81% · 22.4°C." It shows *"House 2 feels
  different today."* — Gaia's `/companion` message, first line only, ≤120 chars.
- **It is silent by default.** When Gaia has nothing worth saying, the HUD shows nothing. Silence is
  the product, not a gap.
- **Tap** the temple to acknowledge (dismiss the line). **Double-tap** to exit.
- It polls Gaia gently (default 45 s) and only re-renders when the thought *changes* — the BLE render
  queue is slow and attention is precious.

## What's here

```
even-hub-gaia/
├── app.json          # Even Hub manifest (package_id, entrypoint…)
├── package.json      # @evenrealities/even_hub_sdk + vite
├── vite.config.ts    # dev server + a /gaia proxy to the Gaia API (CORS in the simulator)
├── index.html        # entry
├── .env.example      # VITE_GAIA_API_URL / VITE_GAIA_API_KEY
└── src/
    ├── main.ts       # the app: connect, render one line, tap/exit, gentle poll
    └── gaia.ts       # tiny client for GET /api/v1/companion (no reasoning here)
```

## Build, test, upload (you/PC — needs Node + Even login)

```bash
npm install
cp .env.example .env.local            # set VITE_GAIA_API_URL + VITE_GAIA_API_KEY
npm run dev                           # preview in evenhub-simulator → http://localhost:5173
npm run build                         # → dist/
npx @evenrealities/evenhub-cli login  # one-time
npx @evenrealities/evenhub-cli pack app.json dist   # → .ehpk
# then upload the .ehpk via the Even Hub portal (the "Upload package" button)
```

## Honest limits (read before relying on it)

- **Not built/tested here.** This environment has no Node, no Even auth, and no glasses — so this is
  *correct source*, not a verified `.ehpk`. The simulator + a real Gaia API are needed to confirm it.
- **Pin the SDK version.** `package.json` uses `latest` for `@evenrealities/even_hub_sdk`; pin it to
  the published version you build against.
- **Acknowledge is local in v1.** Tap dismisses the line on-device. Wire it to a real ack endpoint
  when the Gaia API exposes one (one line in `gaia.ts`).
- **Voice capture is the next increment, not in v1.** The strongest reason for glasses is letting
  Oskar *speak* an observation in the crop (improves Gaia's *observation of reality*). The Even `asr`
  template (`audioControl` + PCM → STT → text) plus the Gaia API `POST /api/v1/voice-notes` is the
  path; it needs an STT provider/key, so it's deliberately deferred to keep v1 honest and simple.
- **One nursery in v1.** `VITE_GAIA_API_URL`/`KEY` select the Gaia instance. The full Connection
  Manager (many nurseries, ADR-007/009) lands when this graduates from a single configured instance.

## Why this passes the gate (CLAUDE.md §the four questions)

It does not make Gaia smarter — it is a window. But it is the window Oskar would most *miss* (#4),
and it is the surface through which his spoken observations will eventually reach Gaia (#2). It is
worth building, and worth building beautifully — *on real data*. A whisper over fixtures is a demo;
a whisper that is right is indispensable.
