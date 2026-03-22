# Deploy Telegram Shop

## 1. What the target machine needs

### Recommended: Docker deploy
- Docker Engine
- Docker Compose
- Internet access to pull `postgres:16` and `redis:7-alpine`
- Telegram bot token and any payment credentials you want to enable

### Local Python deploy
- Python 3.11
- `pip`
- PostgreSQL 16 if you use Postgres
- Redis 7 if you keep `REDIS_ENABLED=1`

## 2. Files to prepare
- Copy `.env.example` to `.env`
- Fill at minimum:
  - `TOKEN`
  - `OWNER_ID`
  - `PAY_CURRENCY`
  - `ADMIN_USERNAME`
  - `ADMIN_PASSWORD`
  - `SECRET_KEY`
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
- Run migrations before first start. The setup script does this automatically.
- If you deploy without Postgres/Redis, use:
  - `DATABASE_URL=sqlite+aiosqlite:///./data/telegram_shop.db`
  - `REDIS_ENABLED=0`
- `logs/` and `data/` are created automatically.
- Do not copy your current `.env`, `logs/`, or `telegram_shop.db` into public bundles.
