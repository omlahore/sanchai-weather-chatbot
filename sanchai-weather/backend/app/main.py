import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent import agent_executor


load_dotenv()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


app = FastAPI(title="SanchAI Weather Backend")

frontend_origin = os.getenv("APP_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    try:
        result = await agent_executor.ainvoke({"input": payload.message})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Our current agent returns a plain string, but we keep this flexible in
    # case we later switch back to an AgentExecutor-style dict output.
    if isinstance(result, str):
        output = result
    elif isinstance(result, dict):
        output = result.get("output")
        if not isinstance(output, str):
            output = str(output)
    else:
        output = str(result)

    return ChatResponse(answer=output)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


