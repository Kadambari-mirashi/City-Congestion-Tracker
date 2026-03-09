# Deployment

- **Backend:** Deployed to **Render** (Web Service). See “Backend on Render” below. Not deployed by this repo’s workflow.
- **Dashboard:** Deployed to **Cornell Posit Connect** via the GitHub Actions workflow in this repo.

## Backend on Render

Deploy the FastAPI backend manually to Render:

1. Create a **Web Service** on [Render](https://render.com) from this repo.
2. Set **Root Directory** to `backend`.
3. **Build:** `pip install -r requirements.txt`
4. **Start:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. In Render **Environment**, add: `SUPABASE_URL`, `SUPABASE_KEY`, and optionally `OPENAI_API_KEY` or Ollama vars.

Use the Render service URL (e.g. `https://your-app.onrender.com`) as **`BACKEND_BASE_URL`** for the dashboard.

## GitHub secrets (for dashboard deployment to Posit)

The workflow deploys **only the Streamlit dashboard** to Cornell Posit Connect. Add these in **Settings → Secrets and variables → Actions**:

### Required

| Secret | Purpose |
|--------|--------|
| `CONNECT_SERVER` | Cornell Posit Connect URL (e.g. `https://connect.college.edu`). |
| `CONNECT_API_KEY` | API key for deploying to Connect. |
| `BACKEND_BASE_URL` | **Your Render backend URL** (e.g. `https://your-app.onrender.com`). The dashboard calls this for data and AI summary. |

### Optional: update same dashboard app

| Secret | Purpose |
|--------|--------|
| `CONNECT_DASHBOARD_APP_ID` | App ID/GUID of the dashboard content on Connect. If set, future deploys **update** that app instead of creating a new one. |

## How the workflow deploys

1. **Trigger:** Push to `main` or **Actions → Deploy Dashboard to Posit Connect → Run workflow**.
2. **Single job – Deploy Dashboard (Streamlit):**
   - Installs `rsconnect-python`.
   - Writes `dashboard/.env` with `BACKEND_BASE_URL` (your Render URL).
   - Deploys the `dashboard/` folder to Cornell Posit Connect as a Streamlit app with entry point **`app.py`**.

## How to rerun the workflow

- **Manual:** Repo → **Actions** → **Deploy Dashboard to Posit Connect** → **Run workflow** (choose branch, then Run).
- **Automatic:** Push commits to `main`.

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| Dashboard deploy fails (auth) | Verify `CONNECT_SERVER` and `CONNECT_API_KEY` are correct and the key has permission to publish content. |
| Backend (Render) returns 500 or DB errors | In Render Environment, set `SUPABASE_URL` and `SUPABASE_KEY`. Run `infra/schema.sql` and optionally `infra/rls_fix.sql` in Supabase. |
| Dashboard shows “can’t reach backend” or JSONDecodeError | Set `BACKEND_BASE_URL` to your **Render backend URL** (e.g. `https://your-app.onrender.com`), then redeploy the dashboard (rerun workflow). |
| AI summary fails | On Render, add `OPENAI_API_KEY` or Ollama vars. |
| “Module not found” on Connect | Dashboard uses `dashboard/requirements.txt` and entry point `app.py`; don’t remove or rename them. |

## Why a new dashboard app appears on every deploy

Each run can create **new** content on Connect. To **update the same dashboard** instead, add **`CONNECT_DASHBOARD_APP_ID`** (the dashboard app’s GUID from Connect) as a GitHub secret; the workflow will then pass `--app-id` and replace that app.

## Summary

- **Backend:** Hosted on **Render** (deploy manually; not part of this workflow). Set env vars on Render.
- **Dashboard:** Deployed to **Cornell Posit Connect** by this workflow. Set `BACKEND_BASE_URL` to your Render URL.
