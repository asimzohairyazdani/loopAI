
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="RAG POC")

app.include_router(router)
