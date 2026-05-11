# Legal Graph Word Add-in

Side panel chat add-in for Microsoft Word. The task pane calls the local FastAPI endpoint at `http://127.0.0.1:8000/chat`, which invokes the compiled LangGraph graph.

## Run locally

Start the LangGraph API from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn agente.api:app --host 127.0.0.1 --port 8000 --reload
```

In another terminal, start the add-in frontend:

```powershell
cd word-addin
npm install
npm run serve
```

In a third terminal, expose it over trusted local HTTPS for Office:

```powershell
cd word-addin
npm run dev
```

Then sideload `manifest.xml` in Word desktop. For local development, prefer a shared folder catalog or the Office sideload tooling. Word on the web normally cannot reach your local `localhost` add-in.

The task pane URL is `https://localhost:3000/taskpane.html`.

The add-in keeps memory by sending the same `thread_id` to FastAPI. Use the `+` button to start a new graph thread.
