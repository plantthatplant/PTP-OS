// Gaia on Even G2 — the One Thought.
// Show a single line of Gaia's judgement when it matters; stay silent the rest of the day.
// This file holds NO greenhouse intelligence — it renders what the Gaia API decides to say.

import {
  waitForEvenAppBridge,
  TextContainerProperty,
  CreateStartUpPageContainer,
  TextContainerUpgrade,
  OsEventTypeList,
} from '@evenrealities/even_hub_sdk'
import { fetchThought } from './gaia'

const POLL_MS = (Number(import.meta.env.VITE_GAIA_POLL_SECONDS) || 45) * 1000
const MAX_CHARS = 120 // one thought, not a paragraph
const statusEl = document.getElementById('status')
const phone = (s: string) => { if (statusEl) statusEl.textContent = s }

// One line, judgement only. Take the first line, trim hard.
function oneThought(message: string): string {
  const first = (message || '').trim().split('\n')[0].trim()
  return first.length > MAX_CHARS ? first.slice(0, MAX_CHARS - 1) + '…' : first
}

const bridge = await waitForEvenAppBridge()
phone('Gaia — connected. Quiet until something matters.')

// A single text container fills the G2 canvas (576×288). It starts EMPTY — silence is the default.
const container = new TextContainerProperty({
  xPosition: 0, yPosition: 0, width: 576, height: 288,
  borderWidth: 0, borderColor: 5, paddingLength: 8,
  containerID: 1, containerName: 'gaia', content: '', isEventCapture: 1,
})
const created = await bridge.createStartUpPageContainer(
  new CreateStartUpPageContainer({ containerTotalNum: 1, textObject: [container] }),
)
if (created !== 0) phone(`Could not draw on the glasses (code ${created}).`)

// --- rendering (debounced; the BLE queue is slow, and attention is precious) ---
let shown = ''            // what is currently on the HUD
let wanted = ''           // what we want on the HUD
let renderTimer: number | null = null
function render(line: string) {
  wanted = line
  if (renderTimer !== null) return
  renderTimer = window.setTimeout(async () => {
    renderTimer = null
    if (wanted === shown) return
    shown = wanted
    await bridge.textContainerUpgrade(
      new TextContainerUpgrade({ containerID: 1, containerName: 'gaia', content: shown }),
    )
  }, 150)
}

// --- the One Thought loop ---
let dismissed = ''        // the exact (full) message the grower has acknowledged (tap)
let currentMessage = ''   // the full message currently behind the line on screen
async function tick() {
  const t = await fetchThought()
  // Silent unless Gaia has a fresh, unacknowledged judgement worth the interruption.
  if (!t || !t.message || t.acknowledged || t.message === dismissed) {
    currentMessage = ''
    render('')             // empty content → the glasses go quiet
    return
  }
  currentMessage = t.message
  render(oneThought(t.message))
}
tick()
const loop = window.setInterval(tick, POLL_MS)

// --- input: tap = acknowledge (dismiss), double-tap = exit ---
let cleaned = false
function cleanup() {
  if (cleaned) return
  cleaned = true
  window.clearInterval(loop)
  unsubscribe()
}

const unsubscribe = bridge.onEvenHubEvent((event: any) => {
  // CLICK_EVENT is 0 and protobuf omits zero fields → coalesce with ?? 0.
  const sys = event.sysEvent?.eventType ?? 0
  const txt = event.textEvent?.eventType ?? 0

  if (sys === OsEventTypeList.DOUBLE_CLICK_EVENT || txt === OsEventTypeList.DOUBLE_CLICK_EVENT) {
    bridge.shutDownPageContainer(1)   // exit the app
    return
  }
  if (sys === OsEventTypeList.CLICK_EVENT || txt === OsEventTypeList.CLICK_EVENT) {
    if (currentMessage) dismissed = currentMessage   // acknowledge the thought on screen
    render('')                                       // go quiet immediately
    phone('Acknowledged.')
    // (When the Gaia API exposes an acknowledge endpoint, POST it here too — one line in gaia.ts.)
    return
  }
  if (sys === OsEventTypeList.SYSTEM_EXIT_EVENT || sys === OsEventTypeList.ABNORMAL_EXIT_EVENT) {
    cleanup()
  }
})

window.addEventListener('beforeunload', cleanup)
