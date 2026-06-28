// The tiny window into Gaia. NO reasoning here — it only fetches Gaia's one thought.
// All intelligence lives behind the Gaia API (ADR-005/006).

const DIRECT = (import.meta.env.VITE_GAIA_API_URL as string) || ''
// In the dev simulator we go through the Vite /gaia proxy (CORS); on device, direct.
const BASE = import.meta.env.DEV ? '/gaia' : DIRECT
const KEY = (import.meta.env.VITE_GAIA_API_KEY as string) || ''

export interface Thought {
  message: string            // the judgement, in human words — what to render
  urgency?: string           // calm | normal | urgent (Gaia decides; we only obey silence)
  confidence?: string
  acknowledged?: boolean
}

/** GET /api/v1/companion → Gaia's single current message, or null if unreachable/silent. */
export async function fetchThought(): Promise<Thought | null> {
  try {
    const res = await fetch(`${BASE}/api/v1/companion`, {
      headers: KEY ? { Authorization: `Bearer ${KEY}` } : {},
    })
    if (!res.ok) return null
    const d: any = await res.json()
    const message = (d.message ?? d.companion ?? d.brief ?? '').toString()
    return { message, urgency: d.urgency, confidence: d.confidence, acknowledged: d.acknowledged }
  } catch {
    return null // unreachable: stay honestly silent, never invent a line
  }
}
