// Gaia on Even G2 — Morning Brief + talk to Gaia.
//
// On launch:  "Gaia is connected." → "Good morning, Oskar." → the real Morning Brief.
// Then:       single tap = talk to Gaia (tap to start listening, tap again to ask)
//             double tap = exit
//
// Holds NO intelligence. Speech and reasoning happen on the Gaia server; this only captures
// the mic, ships the audio, and renders Gaia's answer. Honest when anything is unavailable.

import {
  waitForEvenAppBridge,
  TextContainerProperty,
  CreateStartUpPageContainer,
  TextContainerUpgrade,
  OsEventTypeList,
  AudioInputSource,
} from '@evenrealities/even_hub_sdk'

const API_BASE = (import.meta.env.VITE_GAIA_API_URL as string) || '/gaia'
const API_KEY = (import.meta.env.VITE_GAIA_API_KEY as string) || 'gaia-dev-key'
const CONTAINER_ID = 1

type Mode = 'brief' | 'listening' | 'thinking'
let mode: Mode = 'brief'
let pcmChunks: Uint8Array[] = []

const bridge = await waitForEvenAppBridge()

await bridge.createStartUpPageContainer(
  new CreateStartUpPageContainer({
    containerTotalNum: 1,
    textObject: [
      new TextContainerProperty({
        xPosition: 0, yPosition: 0, width: 576, height: 288,
        borderWidth: 0, borderColor: 5, paddingLength: 4,
        containerID: CONTAINER_ID, containerName: 'gaia',
        content: 'Gaia is connected.', isEventCapture: 1,
      }),
    ],
  }),
)

async function render(text: string): Promise<void> {
  await bridge.textContainerUpgrade(
    new TextContainerUpgrade({ containerID: CONTAINER_ID, containerName: 'gaia', content: text }),
  )
}
const wait = (ms: number) => new Promise<void>((r) => setTimeout(r, ms))

// Fetch with a hard timeout — a hung server then fails gracefully ("unavailable")
// instead of leaving the HUD stuck on "Thinking…".
async function fetchT(url: string, opts: RequestInit, ms: number): Promise<Response> {
  const ctrl = new AbortController()
  const t = setTimeout(() => ctrl.abort(), ms)
  try {
    return await fetch(url, { ...opts, signal: ctrl.signal })
  } finally {
    clearTimeout(t)
  }
}

// --- the Morning Brief (GET /api/v1/morning) ---
async function fetchMorningBrief(): Promise<string | null> {
  try {
    const res = await fetchT(`${API_BASE}/api/v1/morning`,
      { headers: { Authorization: `Bearer ${API_KEY}` } }, 15000)
    if (!res.ok) return null
    const d: any = await res.json()
    return [
      `${d.greenhouse ?? 'Greenhouse'} — Morning Brief`,
      d.brief ?? d.priority ?? '',
      d.first_recommendation ? `Do first: ${d.first_recommendation}` : '',
      'Tap to ask Gaia · double-tap to exit',
    ].filter(Boolean).join('\n')
  } catch {
    return null
  }
}

async function openingSequence(): Promise<void> {
  await wait(1500)
  await render('Good morning, Oskar.')
  await wait(1500)
  const brief = await fetchMorningBrief()
  await render(brief ?? 'Gaia is connected,\nbut the Morning Brief is unavailable.\nTap to ask · double-tap to exit')
}
openingSequence()

// --- talk to Gaia (POST /api/v1/ask with the captured mic audio) ---
function concatPcm(chunks: Uint8Array[]): Uint8Array {
  const total = chunks.reduce((n, c) => n + c.length, 0)
  const out = new Uint8Array(total)
  let off = 0
  for (const c of chunks) { out.set(c, off); off += c.length }
  return out
}

async function askGaia(pcm: Uint8Array): Promise<string> {
  try {
    const res = await fetchT(`${API_BASE}/api/v1/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/octet-stream', Authorization: `Bearer ${API_KEY}` },
      // concatPcm returns a fresh, fully-owned buffer — send it directly.
      body: pcm.buffer as ArrayBuffer,
    }, 75000)   // server caps Whisper(30s)+Claude(60s); allow headroom, then fail gracefully
    if (!res.ok) return 'Gaia is unavailable right now.'
    const d: any = await res.json()
    return (d.answer || 'Gaia had no answer.').toString()
  } catch {
    return 'Gaia is unavailable right now.'
  }
}

async function startListening(): Promise<void> {
  mode = 'listening'
  pcmChunks = []
  await render('Listening… tap to ask.')
  await bridge.audioControl(true, AudioInputSource.Glasses)
}

async function stopAndAsk(): Promise<void> {
  mode = 'thinking'
  await bridge.audioControl(false)
  await render('Thinking…')
  const answer = await askGaia(concatPcm(pcmChunks))
  pcmChunks = []
  mode = 'brief'
  await render(answer)
}

// --- input + audio routing ---
let cleaned = false
function cleanup() {
  if (cleaned) return
  cleaned = true
  bridge.audioControl(false)
  unsubscribe()
}

const unsubscribe = bridge.onEvenHubEvent((event) => {
  // Mic frames arrive here too — collect them only while listening.
  const pcm = event.audioEvent?.audioPcm
  if (pcm && mode === 'listening') { pcmChunks.push(pcm); return }

  const sysType = event.sysEvent?.eventType ?? null
  const textType = event.textEvent?.eventType ?? null

  if (sysType === OsEventTypeList.DOUBLE_CLICK_EVENT || textType === OsEventTypeList.DOUBLE_CLICK_EVENT) {
    bridge.shutDownPageContainer(1)
    return
  }
  if ((sysType ?? 0) === OsEventTypeList.CLICK_EVENT || (textType ?? 0) === OsEventTypeList.CLICK_EVENT) {
    if (mode === 'brief') startListening()
    else if (mode === 'listening') stopAndAsk()
    // ignore taps while thinking
    return
  }
  if (sysType === OsEventTypeList.SYSTEM_EXIT_EVENT || sysType === OsEventTypeList.ABNORMAL_EXIT_EVENT) {
    cleanup()
  }
})

window.addEventListener('beforeunload', cleanup)
