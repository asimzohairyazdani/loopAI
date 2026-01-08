# from fastapi import FastAPI
# import app.api.routes as routes

# app = FastAPI(title="RAG POC")

# app.include_router(routes.router)

#main.py
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="RAG POC")

app.include_router(router)
