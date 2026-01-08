# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel

# from app.services.rag import answer

# router = APIRouter()


# class Query(BaseModel):
#     question: str


# @router.post("/chat")
# def chat(query: Query):
#     if not query.question.strip():
#         raise HTTPException(400, "Question cannot be empty")

#     return {"answer": answer(query.question)}

#routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rag import answer_question
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("API")


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    logger.info(f"Question received: {request.question}")

    return {
        "answer": answer_question(request.question)
    }
