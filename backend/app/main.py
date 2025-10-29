from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, giveaways
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GiveHub API")

# CORS - permitir el frontend estático en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(giveaways.router)

@app.get("/")
def root():
    return {"message": "Bienvenido a GiveHub API"}

@app.get("/server-time")
def get_server_time():
    from datetime import datetime
    return {"utc": datetime.utcnow().isoformat(), "timestamp": datetime.utcnow().timestamp()}
