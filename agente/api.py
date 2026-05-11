from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agente.controllers.admin_controller import router as admin_router
from agente.data.database import get_db, init_db
from backend.data.normative_repository import NormativeRepository
from agente.graph import get_chat_graph


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    thread_id: str = "default"
    document_text: str = ""


class ChatResponse(BaseModel):
    response: str


class HealthResponse(BaseModel):
    status: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    try:
        init_db()
        NormativeRepository(db).seed()
    finally:
        db.close()
    yield


app = FastAPI(title="Legal Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000",
        "http://127.0.0.1:3000",
        "https://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)


@app.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result: dict[str, Any] = get_chat_graph().invoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config={
                "configurable": {
                    "thread_id": request.thread_id,
                    "document_text": request.document_text,
                }
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider error: {exc}",
        ) from exc

    return ChatResponse(response=result["messages"][-1].content)
