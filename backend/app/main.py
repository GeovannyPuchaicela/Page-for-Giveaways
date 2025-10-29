from fastapi import FastAPI
from .routers import users, giveaways

app = FastAPI(title="GiveHub API")

# Rutas principales
app.include_router(users.router)
app.include_router(giveaways.router)

@app.get("/")
def root():
    return {"message": "Bienvenido al sorteo de GiveHub!"}
