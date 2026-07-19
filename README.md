# GenAI Resource Allocation Assistant

PoC chatbot that lets project managers find the best-matching employees via natural-language search, using Gemini for query understanding/summaries and FAISS for semantic skill matching.

## Stack
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- AI: Gemini 2.5 Flash (chat) + `text-embedding-004` (embeddings) + FAISS
- Frontend: React + Vite + Material UI + Recharts

## Run locally

### 1. Backend
```
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # then fill in DATABASE_URL and GEMINI_API_KEY
```
Create the Postgres database referenced in `DATABASE_URL` (default name `genai_resource_allocation`), then seed sample data:
```
python -m app.seed
```
Start the API:
```
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```
cd frontend
npm install
npm run dev
```
Visit http://localhost:5173. The Vite dev server proxies `/api` to `http://localhost:8000` (see `vite.config.js`), so no `.env` is needed locally.

Login is a dummy PoC login — any email/password works. An email containing `rm` (e.g. `rm@company.com`) logs in as Resource Manager, anything else as Project Manager.

## Deploy to production (Render backend + Vercel frontend)

### Backend on Render
1. Push this repo to GitHub.
2. In Render: New → Blueprint, point it at the repo — it will pick up `backend/render.yaml`, which provisions a free Postgres database and a web service.
   - Alternatively, create the web service manually: root directory `backend`, build command `pip install -r requirements.txt`, start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. Set environment variables on the web service:
   - `DATABASE_URL` — from the Render Postgres instance (use the **Internal Database URL**, and change its scheme prefix to `postgresql+psycopg2://`)
   - `GEMINI_API_KEY` — your Gemini API key
   - `JWT_SECRET` — any random string
   - `CORS_ORIGINS` — your Vercel frontend URL once you have it, e.g. `https://your-app.vercel.app`
4. Deploy, then run the seed script once via Render's Shell tab: `python -m app.seed`

Note: Render's free-tier filesystem is ephemeral — the FAISS index file gets rebuilt by `app.seed` and by `/uploadResume`, but a redeploy wipes it. Re-run `python -m app.seed` after a redeploy, or upgrade to a paid plan with a persistent disk mounted at `FAISS_INDEX_PATH`'s directory.

### Frontend on Vercel
1. In Vercel: New Project → import the repo, set root directory to `frontend`.
2. It will auto-detect Vite (build command `npm run build`, output `dist`) — `vercel.json` is already included for SPA routing.
3. Set environment variable `VITE_API_URL` to your Render backend's URL, e.g. `https://genai-resource-allocation-api.onrender.com`.
4. Deploy. Once live, copy the Vercel URL back into Render's `CORS_ORIGINS` env var and redeploy the backend.

## API endpoints
`POST /login` · `POST /uploadResume` · `GET /employees` · `POST /searchCandidates` · `GET /employee/{id}` · `POST /shortlist` · `GET /shortlist` · `GET /analytics`
