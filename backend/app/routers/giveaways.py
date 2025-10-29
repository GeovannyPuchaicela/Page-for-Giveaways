from fastapi import APIRouter

router = APIRouter(prefix="/giveaways", tags=["Giveaways"])

@router.get("/")
def get_giveaways():
    return {"message": "Lista de sorteos activos"}
