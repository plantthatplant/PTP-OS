# Deploying Gaia to a public URL (for Lovable + off-LAN glasses)

The hosted Lovable Control Center and any off-greenhouse glasses need a **public
`https://…/api/v1`** to reach Gaia — a browser served over HTTPS can't call `http://localhost`.
This is that deployment. The API is stdlib Python (no dependencies), so the image is tiny and
the host can be anything that runs a container.

## Security first (the API key rides in the browser)

The Lovable frontend sends the API key from the browser, so **treat it as semi-public**. Before
exposing anything:

1. **Set a strong `GAIA_API_KEY`** (not `gaia-dev-key`). Generate one: `openssl rand -hex 32`.
2. **Pin CORS** to your Lovable origin: `GAIA_CORS_ORIGINS=https://<your-lovable-app>` (and add the
   Even Hub origin if the glasses call it directly). Other origins then get no CORS headers.
3. **`/ask` spends OpenAI + Anthropic money per call.** It is rate-limited per IP
   (`GAIA_ASK_RATE_PER_MIN`, default 30; set lower for a public deploy, `0` to disable). The
   Lovable Control Center does **not** use `/ask` — if you only need Lovable, you can set
   `GAIA_ASK_RATE_PER_MIN` low. Keep your OpenAI/Anthropic keys as host **secrets**, never in the
   image or the repo.

## Option A — Fly.io (recommended: always-on, simple volume)

The repo ships a [`Dockerfile`](../Dockerfile) and [`fly.toml`](../fly.toml).

```bash
fly launch --no-deploy            # accept the existing fly.toml; pick a unique app name + region (arn = Stockholm)
fly volumes create gaia_data --size 1     # persists Memory / Learning / Observations across deploys

# secrets (never in fly.toml or the repo):
fly secrets set \
  GAIA_API_KEY=$(openssl rand -hex 32) \
  GAIA_CORS_ORIGINS=https://<your-lovable-app> \
  OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-ant-... \
  GAIA_ANSWER_MODEL=claude-sonnet-4-6

fly deploy
fly open /api/v1/health           # should return {"status":"ok",...}
```

Your public base is `https://<app>.fly.dev`. `fly.toml` keeps one machine always running so the
collector loop and `/health` stay live (no scale-to-zero).

## Option B — Render

New **Web Service** from the repo → it detects the `Dockerfile`. Add a **Disk** mounted at
`/data` (set `GAIA_DATA_DIR=/data`, `GAIA_APP_DATA_DIR=/data/app`). Render injects `$PORT`, which
the API honours automatically. Set the same env/secrets as above. The base is
`https://<service>.onrender.com`.

## Connect Lovable

Once `https://<host>/api/v1/health` returns `ok`, give Lovable:

- **Backend URL:** `https://<host>/api/v1`
- **API key:** the `GAIA_API_KEY` you set

The "Gaia is temporarily unavailable" cards become live data. (CORS is already handled; you've
pinned it to the Lovable origin above.)

## The honest gap: getting *real* data to the cloud

A cloud deploy makes the API reachable, but it runs on `GAIA_SOURCE=fixture` (demonstration
data) until a **live Synopta export can reach the host**. Synopta's export lives at the
greenhouse, not in the cloud, so live data needs one of:

- the greenhouse PC syncing exports to a folder the host can read (e.g. an object store / Drive
  mount) with `GAIA_SOURCE=drop-folder`, `GAIA_DROP_PATH=<that folder>`; or
- keeping Gaia **on the greenhouse PC** (next to Synopta) and exposing *that* via a tunnel
  instead of a cloud host.

Either way the file-drop pipeline already works (`DropFolderSource` → `translate.py` → snapshot);
see [`docs/sprint-14-founder-pilot.md`](sprint-14-founder-pilot.md) §6. This is a data-delivery
choice, not missing code.

## Persistence note

Memory / Learning / Observations live under `GAIA_APP_DATA_DIR` and snapshots under
`GAIA_DATA_DIR`. **Mount a volume** for these (the configs above do) or they reset on every
redeploy — the greenhouse's accumulated learning would be lost.
