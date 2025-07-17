from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import uuid4
import os

from main import handle_user_message, FinanceContext

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 会话内存存储（简单演示）
CONVERSATIONS: Dict[str, Dict[str, Any]] = {}

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    agent: str
    reply: str
    context: Dict[str, Any]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # 获取或新建会话
    if not req.conversation_id or req.conversation_id not in CONVERSATIONS:
        conversation_id = uuid4().hex
        ctx = FinanceContext()
        CONVERSATIONS[conversation_id] = {"context": ctx}
    else:
        conversation_id = req.conversation_id
        ctx = FinanceContext(**CONVERSATIONS[conversation_id]["context"])

    # 处理用户消息
    result = handle_user_message(req.message, ctx)
    # 更新会话上下文
    CONVERSATIONS[conversation_id]["context"] = result["context"]

    return ChatResponse(
        conversation_id=conversation_id,
        agent=result["agent"],
        reply=result["reply"],
        context=result["context"]
    )
