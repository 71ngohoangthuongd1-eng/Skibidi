# Deploy Telegram Shop

## 1. What the target machine needs

### Recommended: Docker deploy
- Docker Engine
- Docker Compose
- Internet access to pull `postgres:16` and `redis:7-alpine`
- Telegram bot token, SePay bank account details, and the SePay webhook secret if you want automatic bank transfer confirmation

### Local Python deploy
- Python 3.11
- `pip`
- PostgreSQL 16 if you use Postgres
- Redis 7 if you keep `REDIS_ENABLED=1`
- Install dependencies from `requirements-prod.txt` so `sqladmin`, `uvicorn`, and the bot runtime packages are available

## 2. Files to prepare
- If you are re-deploying onto an existing server, delete the old `.env` first
  so you do not reuse stale secrets or host-specific values.
- Copy `.env.example` to `.env`
- Fill at minimum:
  - `TOKEN`
  - `OWNER_ID`
  - `PAY_CURRENCY`
  - `ADMIN_USERNAME`
  - `ADMIN_PASSWORD`
  - `SECRET_KEY`
  - `SEPAY_BANK_NAME`
  - `SEPAY_ACCOUNT_NO`
  - `SEPAY_WEBHOOK_SECRET`
  - `SEPAY_PAYMENT_PREFIX`
- Choose one database mode:
  - Docker/Postgres: leave `DATABASE_URL=` empty and fill `POSTGRES_*`
  - Simple local SQLite: set `DATABASE_URL=sqlite+aiosqlite:///./data/telegram_shop.db`
- Choose Redis mode:
  - Production: `REDIS_ENABLED=1`
  - Simple local machine: `REDIS_ENABLED=0`

## 3. Fastest install on another machine

### Option A: Docker
1. Copy the project bundle to the other machine
2. Create `.env` from `.env.example`
3. Run:

```powershell
docker compose up -d --build
```

4. The admin panel will be on `http://127.0.0.1:9090`

### Option B: Local Python on Windows
1. Copy the project bundle to the other machine
2. Create `.env` from `.env.example`
3. Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-local.ps1
```

4. Start the bot:

```powershell
.\.venv\Scripts\python.exe run.py
```

### Option C: VS Code on Windows
1. Open the folder in VS Code
2. Install the recommended extensions when prompted
3. Copy `.env.example` to `.env` and fill the real values
4. Use one of these:
   - `Terminal -> Run Task -> Setup Local`
   - `F5` and choose `Run Bot`
   - `Terminal -> Run Task -> Run Tests`
5. Included VS Code files:
   - `.vscode/settings.json`
   - `.vscode/tasks.json`
   - `.vscode/launch.json`

## 4. Notes
- Install from `requirements-prod.txt` on the server so `sqladmin` is present for the admin panel.
- SePay setup needs a public URL for `SEPAY_IPN_PATH` and the matching `SEPAY_WEBHOOK_SECRET`.
- Run migrations before first start. The setup script does this automatically.
- If you deploy without Postgres/Redis, use:
  - `DATABASE_URL=sqlite+aiosqlite:///./data/telegram_shop.db`
  - `REDIS_ENABLED=0`
- `logs/` is tracked in the repo so file logging has a stable target directory.
- `data/` is created automatically.
- Do not copy your current `.env`, `logs/`, or `telegram_shop.db` into public bundles.

## 5. Vercel serverless deploy

The repo ships a Vercel-ready serverless entrypoint (`api/index.py`). The bot runs in
webhook mode: Telegram calls your deployment URL, and PayU recovery / data cleanup are
scheduled with Vercel Cron. There is no long-running Python process.

### Prerequisites
- `vercel` CLI: `npm i -g vercel` and `vercel login`
- An external PostgreSQL (e.g. Neon, `postgresql+asyncpg://...`) — SQLite will not work
  on Vercel's ephemeral filesystem
- Redis (e.g. Upstash) so FSM state and caches survive between cold starts

### 1. Set env vars in Vercel (dashboard or `vercel env add`)
Required every deploy:
- `TOKEN` — Telegram bot token
- `OWNER_ID`
- `DATABASE_URL` — full async SQLAlchemy URL to the external Postgres
- `REDIS_URL` — full `rediss://...` URL (Upstash etc.), used for FSM, cache and rate limiting
- `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `SECRET_KEY`
- `WEBHOOK_ENABLED=1`
- `WEBHOOK_SECRET` — random secret Telegram will send back as `X-Telegram-Bot-Api-Secret-Token`
- `CRON_SECRET` — random secret Vercel Cron sends as `Authorization: Bearer <CRON_SECRET>`
- SePay for bank auto-confirm: `SEPAY_BANK_NAME`, `SEPAY_ACCOUNT_NO`, `SEPAY_ACCOUNT_NAME`,
  `SEPAY_WEBHOOK_SECRET`, `SEPAY_IPN_PATH=/sepay/ipn`, `SEPAY_PAYMENT_PREFIX`

Optional:
- `REDIS_ENABLED=1` — must stay `1` on Vercel; `validate_production()` hard-fails if disabled
- `PAY_CURRENCY`, `MIN_AMOUNT`, `MAX_AMOUNT`, `CHANNEL_URL`, `CHANNEL_ID`, `HELPER_ID`, `RULES`, `BOT_LOCALE`
- Cleanup retention: `AUDIT_RETENTION_DAYS`, `PAYMENTS_RETENTION_DAYS`
- Pool tuning: `DB_POOL_SIZE` (5), `DB_MAX_OVERFLOW` (10), `DB_POOL_RECYCLE` (1800)

Note: `api/index.py` runs `validate_production()` when `VERCEL=1` (set automatically) or
`BOT_MODE=webhook`. It refuses to boot if: SQLite is configured, Redis is disabled, the
admin credentials are the insecure defaults, or `WEBHOOK_ENABLED` is unset on Vercel.
It also refuses to start long-lived polling/webhook servers on serverless.

Warning: the Vercel build runs the default Python (3.12, pinned by `.python-version`),
not your local run's set of workers.

### 2. Deploy
```powershell
vercel --prod
```

### 3. Point Telegram at the webhook
After the deployment succeeds, call once (per environment):
```
GET https://<project>.vercel.app/api/set-webhook
```
This registers `https://<project>.vercel.app/webhook` with the `WEBHOOK_SECRET`.
You can also do it manually: `curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=..."`.

### 4. SePay IPN
Set the IPN webhook in the SePay dashboard to:
```
https://<project>.vercel.app/sepay/ipn
```
with header `X-Secret-Key: <SEPAY_WEBHOOK_SECRET>`. This URL is served by the admin panel
mount, so the admin app must be built (`create_admin_app` runs at import of `api/index.py`).

### 5. Vercel Cron
`vercel.json` defines:
- `/api/cron/cleanup` — once per day at 04:00 UTC (data retention cleanup)

Cron limits to remember:
- Hobby (free): every cron job runs **at most once per day** and only on the production
  deployment — a `*/5 * * * *` recovery cron would be rejected at deploy time.
- Pro / Enterprise: sub-daily schedules allowed; if you need payment recovery more often,
  add it as `/api/cron/recovery` with `*/5 * * * *`.

Both cron endpoints authenticate with `Authorization: Bearer <CRON_SECRET>` (Vercel sends
this when `CRON_SECRET` is set) and are also protected by a distributed Redis lock, so
overlapping invocations are harmless. The recovery endpoint additionally detects and
re-validates stuck `pending` payments.

Payment recovery and cleanup also run automatically at startup of a warm instance only
in polling mode; on Vercel they are driven exclusively by these cron endpoints or by an
external scheduler hitting `/api/cron/recovery`.

### 6. Known serverless trade-offs
- Cold starts re-register handlers and re-create the admin app on demand; the first webhook
  for a warm slot may be slower.
- `logs/` writes are skipped safely on the read-only filesystem (the logger falls back to
  console-only); locale overrides fall back to `/tmp` when the project dir is read-only.
- Do not rely on local filesystem for state — the database is the single source of truth.
- The admin panel is reachable under the same deployment URL (`/admin`), backed by the
  external Postgres; keep `ADMIN_USERNAME`/`ADMIN_PASSWORD` private.
