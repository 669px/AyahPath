# AyahPath

AyahPath is a Flask-based Qur'anic life guidance app. It helps users explore relevant ayat for everyday situations, reflect on personal challenges, track prayer progress, build streaks, save reflections, and view supportive reminders from a local virtual Qur'an dataset.

The project is split into a frontend Flask app and a backend API. Running `app.py` starts both services locally.

## Features

- Daily and personalized ayah cards with Arabic text, English translation, optional secondary translation, and audio links.
- Life-scenario guidance for themes such as stress, anger, jealousy, gratitude, forgiveness, patience, charity, honesty, humility, and trust in Allah.
- Reflection flow that maps user input to a relevant Qur'anic category and returns practical and spiritual guidance.
- Optional OpenRouter-powered AI guidance, with keyword-based fallback when no API key is configured.
- Prayer tracker with daily completion, weekly summary, streaks, total prayers, and completion rate.
- Saved reflections, activity history, goals, streak tracking, notifications, language settings, and theme controls.
- Quran Foundation-compatible local Qur'an API endpoints backed by bundled JSON data, with optional live API credentials.
- SQLite-backed prayer database for local persistence.
- Ubuntu deployment script with Gunicorn, systemd, and Nginx setup.

## Tech Stack

- Python 3
- Flask
- Flask-CORS
- Requests
- python-dotenv
- SQLite
- HTML, CSS, and vanilla JavaScript

## Project Structure

```text
.
+-- app.py                     # Frontend Flask app and integrated local launcher
+-- prayer_db.py               # SQLite prayer tracking helpers
+-- schema.sql                 # Prayer database schema
+-- requirements.txt           # Python dependencies
+-- deploy.sh                  # Ubuntu deployment script
+-- api/
|   +-- app.py                 # Backend API
|   +-- config.py              # Environment/config handling
|   +-- data/                  # Local JSON persistence and Qur'an sample data
|   +-- models/                # Scenario and mapping data
|   +-- services/              # AI, Qur'an, YouTube, and data services
+-- static/
|   +-- css/style.css
|   +-- js/app.js
|   +-- img/logo.png
+-- templates/
    +-- index.html
    +-- 404.html
    +-- 500.html
    +-- 503.html
```

## Local Setup

Clone the repository and enter the project directory:

```bash
git clone <your-repo-url>
cd AyahPath-main
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the integrated launcher:

```bash
python app.py
```

Open the app:

```text
http://localhost:5000
```

The backend API runs on:

```text
http://localhost:5001
```

Health checks:

```text
http://localhost:5000/health
http://localhost:5001/api/health
```

## Windows Console Note

If Windows raises a Unicode encoding error when `app.py` prints startup icons, run with UTF-8 output enabled:

```powershell
$env:PYTHONIOENCODING = "utf-8"
python app.py
```

## Environment Variables

Create a `.env` file in the project root or inside `api/` if you want to override defaults.

```env
FRONTEND_PORT=5000
API_HOST=localhost
API_PORT=5001
API_DEBUG=false
APP_URL=http://localhost:5000
DATA_DIR=data
FLASK_SECRET_KEY=change-this-for-production
AYAHPATH_ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000

# Optional AI integration
OPENROUTER_API_KEY=
AI_MODEL=google/gemini-2.0-flash-001

# Optional Quran Foundation / Quran.com Content API integration
QURAN_CLIENT_ID=
QURAN_CLIENT_SECRET=
QURAN_AUTH_BASE_URL=https://oauth2.quran.foundation
QURAN_API_BASE_URL=https://apis.quran.foundation
QURAN_MCP_BASE_URL=
QURAN_MCP_TIMEOUT_SECONDS=6
QURAN_API_TIMEOUT_SECONDS=12
QURAN_MCP_FAIL_COOLDOWN_SECONDS=300
QURAN_USE_OFFICIAL_API=auto
QURAN_DEFAULT_TRANSLATION=131
QURAN_DEFAULT_RECITATION=7
QURAN_DEFAULT_TAFSIR=169

# Present in config, currently optional
GEMINI_API_KEY=
YOUTUBE_API_KEY=
```

The app works without `OPENROUTER_API_KEY`; it falls back to local keyword matching and built-in guidance.

The app also works without Quran Foundation credentials.
Set `QURAN_MCP_BASE_URL=https://mcp.quran.ai` to fetch verses/translations from Quran MCP's hosted content endpoints first. If MCP is unavailable, the backend falls back to the official OAuth Content API (when credentials are set), then to the bundled virtual Qur'an data.

## Common API Routes

Frontend/proxy routes are served from `app.py`, while backend routes are served from `api/app.py`.

```text
GET    /api/scenarios
GET    /api/scenarios/<scenario_id>
GET    /api/daily-ayah
GET    /api/personalized-ayah
POST   /api/reflections
GET    /api/reflections/<user_id>
DELETE /api/reflections/<reflection_id>
GET    /api/streak
POST   /api/streak/<user_id>/checkin
GET    /api/goals
POST   /api/goals
DELETE /api/goals/<goal_id>
GET    /api/activity
POST   /api/activity
GET    /api/history
DELETE /api/history
GET    /api/quran/chapters
GET    /api/quran/verse/<surah>/<ayah>
GET    /api/quran/tafsir/<surah>/<ayah>
GET    /api/prayers/<date>
POST   /api/prayers/<date>/<prayer_id>
GET    /api/prayers/week
GET    /api/prayers/stats
```

Virtual Qur'an-style endpoints:

```text
GET /content/api/v4/chapters
GET /content/api/v4/verses
GET /content/api/v4/verses/by_key/<verse_key>
GET /content/api/v4/verses/by_chapter/<chapter_number>
GET /content/api/v4/verses/by_page/<page_number>
GET /content/api/v4/verses/by_juz/<juz_number>
GET /content/api/v4/verses/by_category/<category>
GET /content/api/v4/verses/by_keywords?q=<query>
```

`by_category` and `by_keywords` are AyahPath-specific helper endpoints. The other `/content/api/v4/...` routes are shaped to match Quran Foundation Content API patterns as closely as possible while using local data when credentials are not available.

## Data and Persistence

- Prayer tracking is stored in `prayer.db`, initialized from `schema.sql`.
- Reflection, activity, goal, streak, and virtual Qur'an data live under `api/data/`.
- The bundled virtual Qur'an dataset allows the core app to run without depending on an external Qur'an API.

Generated local files such as `.venv/`, `__pycache__/`, logs, and database files should not be committed.

## Deployment

For an Ubuntu 22.04 or 24.04 server, the included deployment script installs system dependencies, creates an application user, configures a virtual environment, initializes SQLite, registers systemd services, and sets up Nginx:

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

After deployment, useful service commands include:

```bash
sudo systemctl status ayahpath-frontend
sudo systemctl status ayahpath-api
sudo journalctl -u ayahpath-frontend -f
sudo journalctl -u ayahpath-api -f
```

## Security Notes

- Set a strong `FLASK_SECRET_KEY` in production.
- Restrict `AYAHPATH_ALLOWED_ORIGINS` to your real domain.
- Keep `.env`, local databases, and runtime logs out of version control.
- Do not expose API keys in client-side code or committed files.

## License

No license file is currently included. Add a license before publishing if you want to define how others may use, modify, or distribute the project.
