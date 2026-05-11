# LegalMind

LegalMind is a local prototype for a Microsoft Word side-panel chat add-in backed by a FastAPI API and a LangGraph graph.

The agent is designed for lawyer clients of LegalTalent, a compliance startup. Its purpose is to help lawyers review contracts by reasoning over the full text of the Word document currently open.

## Project Structure

```text
.
├── backend/
│   ├── api.py                 # FastAPI app and /chat endpoint
│   ├── graph.py               # LangGraph assembly
│   ├── llm.py                 # ChatOpenAI configuration
│   ├── state.py               # Graph state schemas
│   ├── nodos/
│   │   ├── load_document.py   # Loads Word document text from graph config
│   │   └── llm.py             # LegalMind LLM node and system prompts
│   ├── controllers/
│   │   └── admin_controller.py  # Normative source catalog CRUD
│   ├── data/
│   │   ├── database.py          # SQLAlchemy engine and session factory
│   │   └── normative_repository.py  # ORM models and repository
│   ├── schemas/
│   │   └── fuente.py            # Pydantic schemas for normative sources
│   └── modules/               # Placeholders: RAG, ingestion, contract analysis
├── frontend/
│   ├── manifest.xml           # Word add-in manifest
│   └── assets/                # Add-in icons
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Backend Setup

Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=contract-agent

OPENAI_API_KEY=...
OPENAI_MODEL=openai/gpt-oss-20b:free
```

If you are using OpenRouter-compatible model names, `backend/llm.py` automatically uses:

```text
https://openrouter.ai/api/v1
```

when `OPENAI_BASE_URL` is not set.

## Run FastAPI

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
```

Useful URLs:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Chat API

Endpoint:

```http
POST /chat
```

Request body:

```json
{
  "message": "Revisa las clausulas de terminacion",
  "thread_id": "word-session-1",
  "document_text": "Texto completo del contrato..."
}
```

Response:

```json
{
  "response": "..."
}
```

`thread_id` controls LangGraph memory. Reuse the same value to keep a conversation. Use a new value to start a new conversation.

## LangGraph Design

The graph is:

```text
START -> load_document -> llm -> END
```

The graph uses:

- `LegalMindState`: internal state, includes `messages` and `document_text`.
- `ChatInputState`: public graph input, only chat messages.
- `ChatOutputState`: public graph output, only chat messages.
- `InMemorySaver`: short-term memory while the FastAPI process is running.

`document_text` is passed through `config.configurable`, not as public graph input. This keeps LangSmith top-level graph traces focused on user input and model output instead of showing the whole contract as the run input/output.

Current limitation: memory is in-process only. Restarting Uvicorn clears graph memory. For persistent memory, replace `InMemorySaver` with a SQLite or Postgres checkpointer.

## Word Add-in Setup

Install Node dependencies:

```powershell
cd frontend
npm install
```

Validate the manifest:

```powershell
npm run validate
```

Start the static add-in files:

```powershell
npm run serve
```

In another terminal, start the local HTTPS proxy required by Office:

```powershell
npm run dev
```

The task pane should be available at:

```text
https://localhost:3000/taskpane.html
```

Then sideload:

```text
frontend/manifest.xml
```

Use Word desktop for local development. Word on the web usually cannot reach a localhost add-in.

## How The Add-in Uses The Document

`word-addin/taskpane.js` reads the open Word document with Office.js:

```js
Word.run(async (context) => {
  const body = context.document.body;
  body.load("text");
  await context.sync();
  return body.text || "";
});
```

On every chat message, the add-in sends:

- the user message,
- the current `thread_id`,
- the full current Word document text as `document_text`.

The graph injects that document text as context for LegalMind before calling the LLM.

## Development Notes

- Do not commit `.env`.
- Do not commit `frontend/node_modules/`.
- After backend code changes, restart Uvicorn unless running with `--reload`.
- After manifest changes, re-run `npm run validate` and reload/sideload the manifest in Word.
- If the add-in cannot call FastAPI, check CORS in `backend/api.py` and confirm FastAPI is running on `127.0.0.1:8000`.

## Quick Smoke Tests

Backend import:

```powershell
.\.venv\Scripts\python.exe -c "from backend.graph import get_chat_graph; print(type(get_chat_graph()).__name__)"
```

Health check:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```

Chat check:

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/chat `
  -Method Post `
  -ContentType 'application/json' `
  -Body '{"message":"responde solo ok","thread_id":"smoke-test","document_text":"Contrato de prueba"}'
```
