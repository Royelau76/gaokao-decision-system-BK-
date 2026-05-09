# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

云志选 (Yun Zhi Xuan) — 2026年云南省高考志愿填报智能决策支持系统. A web-based platform for Yunnan Gaokao (college entrance exam) decision support, providing intelligent university-major recommendations based on historical admission data.

**Stack**: React 18 + Ant Design 5 | FastAPI + Pydantic v2 | SQLite

## Development Commands

```bash
# Backend (from backend/)
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (from frontend/)
npm install --legacy-peer-deps   # required for antd 5 peer dep conflicts
npm start                        # dev server at :3000, proxies /api to :8000

# Build frontend
npm run build

# Run backend tests
cd backend && python -m pytest tests/ -v
```

## Architecture

### Backend (`backend/`)

**Database**: SQLite at `backend/data/gaokao.db`. All DB access goes through `backend/db.py`:
- `get_db_path()` — returns path, ensures directory exists
- `get_connection()` — returns connection with `row_factory = sqlite3.Row` (dict-like access)
- NEVER use raw `sqlite3.connect()` anywhere else

**Main app** (`main.py`): FastAPI with `lifespan` context manager (NOT deprecated `on_event`). Five routers registered:

| Router | Prefix | Module | Purpose |
|---|---|---|---|
| yunnan_physics_router | `/api/yunnan` | `yunnan_physics_api.py` | 云南物理类分数线 query/recommend |
| yunnan_segments_router | `/api/yunnan/segments` | `yunnan_score_segments_api.py` | 一分一段表 queries |
| yunnan_b_segment_router | `/api/yunnan/b-segment` | `yunnan_plan_api.py` | 招生计划 queries (backward-compat prefix) |
| query_router | `/api/query` | `query_api.py` | User-facing search (by-school, by-rank, by-plan) |
| data_entry_router | `/api/data-entry` | `data_entry_api.py` | Full CRUD: scores, segments, plans, universities + batch CSV import |

**Key DB tables**: `universities`, `yunnan_physics_scores`, `yunnan_physics_score_segments`, `yunnan_plan_data` (replaces `yunnan_b_segment_plans`, has `batch_type` column), `admission_scores`, `students`, `volunteer_plans`

**Pydantic v2**: Use `model_dump()` NOT the deprecated `dict()`. Score fields use `float` (not `int`) because real data has fractional averages.

### Frontend (`frontend/src/`)

Single-page React app with state-based routing (no React Router). All navigation via `useState('home')` in `App.js`.

**Page structure** (`App.js`):
- `home` → `HomePage` — feature cards (查询, 志愿填报, 数据录入)
- `query` → `QueryPanel` — 3 tabs: 按院校专业, 按位次, 按招生计划
- `simulator` → `SimulatorPage` — 4-step wizard (录入→推荐→方案→导出)
- `data-entry` → `DataEntry` — 4 tabs: 录取分数, 一分一段, 招生计划, 院校管理

**Component pattern**: Each data-entry tab is an independent component with its own state, year filter, CRUD modal, CSV import/export, and Ant Design Table. API calls go to `/api/data-entry/*`. The `/api/query/*` prefix serves user-facing search.

**Proxy**: `frontend/package.json` has `"proxy": "http://localhost:8000"` so `/api/*` calls in dev are forwarded to the backend.

### Score-to-Rank Conversion

Score-to-rank conversion is now DB-backed via `yunnan_physics_score_segments` table. The API endpoint `/api/score-conversion` accepts optional `year` param and returns `{score, estimated_rank, year_used}`. Frontend calls this API directly (no dual hardcoding).

## Critical Notes

- **npm install must use `--legacy-peer-deps`** due to `@ant-design/charts` vs `@ant-design/icons` version conflict
- **CI uses `npm install --legacy-peer-deps`** (NOT `npm ci`) because the lockfile was generated with a newer npm
- The `data/` directory at repo root is **NOT** the working database — it's legacy. The active DB is `backend/data/gaokao.db`
- Ant Design 5: use `items` prop on Tabs (NOT `Tabs.TabPane` which is removed)
- All recommendation queries use rank-based comparison (min_rank ranges), not score-offset
