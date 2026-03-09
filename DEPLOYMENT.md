# Deployment to Posit Connect

This project deploys two apps to your college Posit Connect server via GitHub Actions: the **FastAPI backend** first, then the **Streamlit dashboard**.

## GitHub secrets

### Already configured (you added these)

| Secret | Used by | Purpose |
|--------|--------|--------|
| `CONNECT_SERVER` | Workflow | Posit Connect server URL (e.g. `https://connect.college.edu`). |
| `CONNECT_API_KEY` | Workflow | API key for deploying to Connect. |

### Secrets you must add

Add these in **Settings → Secrets and variables → Actions** so the deployed apps can run correctly.

**Backend (required for DB and optional for AI):**

| Secret | Required | Purpose |
|--------|----------|--------|
| `SUPABASE_URL` | Yes | Supabase project URL. Backend needs this to read locations and congestion data. |
| `SUPABASE_KEY` | Yes | Supabase anon or service role key. |
| `OPENAI_API_KEY` | No* | OpenAI API key if you use OpenAI for AI summaries. |
| `OLLAMA_HOST` | No* | e.g. `https://ollama.com` for Ollama Cloud. |
| `OLLAMA_API_KEY` | No* | Required for Ollama Cloud. |
| `OLLAMA_MODEL` | No* | e.g. `gpt-oss:20b-cloud`. |

\* Use either OpenAI or Ollama; the backend uses whichever is configured.

**Dashboard (required after backend is live):**

| Secret | Required | Purpose |
|--------|----------|--------|
| `BACKEND_BASE_URL` | Yes (after 1st deploy) | Full URL of the deployed backend on Connect (e.g. `https://connect.college.edu/content/1234/`). The dashboard calls this for data and AI summary. |

## How the workflow deploys

1. **Trigger:** Runs on every **push to `main`** and can be run manually via **Actions → Deploy to Posit Connect → Run workflow**.
2. **Backend job:**
   - Installs `rsconnect-python`.
   - Writes `backend/.env` from the backend secrets above (so the deployed app has Supabase and AI config).
   - Deploys the `backend/` folder to Connect as a **FastAPI** app with entry point **`main:app`**.
3. **Dashboard job** (runs after backend succeeds):
   - Installs `rsconnect-python`.
   - Writes `dashboard/.env` with `BACKEND_BASE_URL` so the dashboard knows where the API is.
   - Deploys the `dashboard/` folder to Connect as a **Streamlit** app with entry point **`app.py`**.

Backend is always deployed first so that when the dashboard runs, you can point it at the backend URL you get from the first run (or a previous run).

## Manual step after the first backend deployment

1. After the **first** backend deploy, open the deployed backend app on Posit Connect and copy its **full URL** (e.g. `https://connect.college.edu/content/1234/`).
2. Add or update the **`BACKEND_BASE_URL`** repository secret with that URL (no trailing slash is fine).
3. Re-run the workflow (or push a small change) so the dashboard job runs again and deploys the dashboard with the correct `BACKEND_BASE_URL`. Until then, the dashboard may be deployed but will fail or show errors when calling the API if it still has the default/local URL.

## How to rerun the workflow

- **Manual:** Repo → **Actions** → **Deploy to Posit Connect** → **Run workflow** (choose branch, then Run).
- **Automatic:** Push commits to `main`.

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| Backend deploy fails (auth) | Verify `CONNECT_SERVER` and `CONNECT_API_KEY` are correct and the key has permission to publish content. |
| Backend returns 500 or DB errors | Ensure `SUPABASE_URL` and `SUPABASE_KEY` are set. Run `infra/schema.sql` and optionally `infra/rls_fix.sql` in Supabase if tables/RLS are not set up. |
| Dashboard shows “can’t reach backend” | Set `BACKEND_BASE_URL` to the **exact** URL of the deployed backend app (including `/content/...`), then redeploy the dashboard (rerun workflow or push). |
| AI summary fails on Connect | Configure either `OPENAI_API_KEY` or `OLLAMA_HOST` + `OLLAMA_API_KEY` (and optionally `OLLAMA_MODEL`). For Ollama Cloud, use `OLLAMA_HOST=https://ollama.com`. |
| “Module not found” on Connect | Backend and dashboard each use their own `requirements.txt` and are deployed from `backend/` and `dashboard/`; ensure you didn’t remove or rename `main.py` / `app.py` or change the entry points in the workflow. |

## Summary

- **Backend:** Deployed from `backend/` with `main:app`. Needs Supabase (and optionally OpenAI or Ollama) via secrets.
- **Dashboard:** Deployed from `dashboard/` with `app.py`. Needs `BACKEND_BASE_URL` set to the live backend URL after the first backend deploy.
- Add the required and optional secrets above, then run the workflow; after the first backend deploy, set `BACKEND_BASE_URL` and rerun so the dashboard uses the correct API.
