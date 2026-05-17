# AI QA Automation Web Platform with Self-Healing Selenium Engine

Production-oriented MVP for AI-assisted QA automation. The platform generates structured test cases, executes Selenium/PyTest-style steps, captures failure context, attempts self-healing locator recovery, and displays execution history in a React dashboard.

## Architecture

```text
Frontend React dashboard
  -> FastAPI backend
    -> AI test generator
    -> execution controller
    -> Selenium runner
    -> failure detector
    -> self-healing engine
    -> JSON storage and reports
```

## MVP Features

- Website URL and feature input
- AI test generation interface with deterministic local fallback
- Positive, negative, and edge test cases
- Selenium execution engine with demo mode
- Failure context model for broken locators
- Ranked self-healing selector recovery
- JSON project and report storage
- Execution dashboard with passed, failed, and healed statuses
- JSON report download endpoint

## Project Structure

```text
qa-ai-web-platform/
├── backend/
│   ├── main.py
│   ├── ai/test_generator.py
│   ├── core/
│   │   ├── executor.py
│   │   ├── failure_detector.py
│   │   ├── reporting.py
│   │   ├── selenium_runner.py
│   │   └── self_healing.py
│   ├── models/schemas.py
│   └── storage/json_store.py
├── frontend/
│   └── src/
├── reports/
├── tests/
└── requirements.txt
```

## Backend Setup

```powershell
cd qa-ai-web-platform
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open API docs at `http://127.0.0.1:8000/docs`.

## API Security

Set `QA_PLATFORM_API_KEY` in `.env` to require `X-API-Key` on all project, execution, logs, results, and report download endpoints. Leave it unset only for local demos.

```powershell
$env:QA_PLATFORM_API_KEY = "use-a-long-random-secret"
$env:CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
```

Frontend requests send the key from `frontend/.env`:

```powershell
cd frontend
Copy-Item .env.example .env
```

Keep `.env` files out of Git. The repository includes only `.env.example` templates.

## Frontend Setup

```powershell
cd qa-ai-web-platform\frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open the dashboard at `http://127.0.0.1:5173`.

## API Endpoints

- `POST /generate-tests`
  - Input: `{ "url": "https://example.com", "feature": "login form validation" }`
  - Output: `project_id` and structured test cases
- `POST /run-tests`
  - Input: `{ "project_id": "...", "headless": true, "demo_mode": true }`
  - Output: execution report
- `GET /results/{project_id}`
  - Returns latest report for the project
- `GET /logs/{test_id}`
  - Returns step logs for a test case
- `GET /reports/{project_id}/download`
  - Downloads JSON report

## AI Integration

`backend/ai/test_generator.py` is intentionally isolated. Add an OpenAI or Claude structured-output call there and keep the same `list[TestCase]` return contract.

Recommended production prompt contract:

```text
Return JSON only. Generate positive, negative, and edge Selenium test cases for the URL and feature. Include action, selector, value, expected behavior, and severity.
```

## Selenium Mode

The dashboard calls `/run-tests` with `demo_mode: true` so the end-to-end workflow runs without ChromeDriver setup. Set `demo_mode: false` in `frontend/src/api/client.js` or call the API directly to use real Selenium execution.

Real Selenium mode expects:

- Chrome installed
- Selenium Manager or ChromeDriver available
- Target website reachable from the backend machine

## Scalable Storage Path

The MVP uses JSON files under `backend/storage_data` and exported reports under `reports`. The model layer is already typed with Pydantic, so moving to SQLite or PostgreSQL means replacing `JsonStore` with a repository backed by SQLAlchemy or SQLModel.

## Build Order Used

1. Selenium runner and execution abstractions
2. FastAPI endpoints
3. AI test generator fallback
4. Reporting and storage
5. React dashboard
6. Self-healing selector recovery
