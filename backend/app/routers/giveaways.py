from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/giveaways", tags=["Giveaways"])

# --- Crear giveaway ---
@router.post("/", response_model=schemas.GiveawayResponse)
def create_giveaway(giveaway: schemas.GiveawayCreate, db: Session = Depends(get_db), current_user: models.User = Depends(utils.get_current_user)):
    new_giveaway = models.Giveaway(
        **giveaway.dict(),
        creator_id=current_user.id
    )
    db.add(new_giveaway)
    db.commit()
    db.refresh(new_giveaway)
    return new_giveaway

# --- Listar giveaways ---
@router.get("/", response_model=list[schemas.GiveawayResponse])
def list_giveaways(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(utils.get_current_user_optional)
):
    giveaways = db.query(models.Giveaway).all()
    
    # Enriquecer cada giveaway con datos del usuario actual
    for giveaway in giveaways:
        if current_user:
            giveaway.is_owner = current_user.id == giveaway.creator_id
            giveaway.has_participated = current_user in giveaway.participants
            giveaway.can_participate = (
                not giveaway.has_participated and
                not giveaway.winner_id and
                current_user.id != giveaway.creator_id and
                giveaway.end_date > datetime.utcnow()
            )
        giveaway.participants_count = len(giveaway.participants)
    
    return giveaways

# --- Obtener giveaway por ID ---
@router.get("/{giveaway_id}", response_model=schemas.GiveawayResponse)
def get_giveaway(
    giveaway_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(utils.get_current_user_optional)
):
    giveaway = db.query(models.Giveaway).filter(models.Giveaway.id == giveaway_id).first()
    if not giveaway:
        raise HTTPException(status_code=404, detail="Giveaway no encontrado")
    
    # Enriquecer respuesta con datos del usuario actual
    if current_user:
        giveaway.is_owner = current_user.id == giveaway.creator_id
        giveaway.has_participated = current_user in giveaway.participants
        giveaway.can_participate = (
            not giveaway.has_participated and
            not giveaway.winner_id and
            current_user.id != giveaway.creator_id and
            giveaway.end_date > datetime.utcnow()
        )
    
    giveaway.participants_count = len(giveaway.participants)
    return giveaway


# --- Participar en un giveaway ---
@router.post("/{giveaway_id}/participate", response_model=schemas.ParticipateResponse)
def participate_in_giveaway(
    giveaway_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(utils.get_current_user)
):
    giveaway = db.query(models.Giveaway).filter(models.Giveaway.id == giveaway_id).first()
    if not giveaway:
        raise HTTPException(status_code=404, detail="Giveaway no encontrado")
    
    # Validaciones
    if giveaway.winner_id:
        raise HTTPException(status_code=400, detail="Este giveaway ya tiene un ganador")
    
    if giveaway.end_date <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Este giveaway ya ha finalizado")
    
    if current_user.id == giveaway.creator_id:
        raise HTTPException(status_code=400, detail="No puedes participar en tu propio giveaway")
    
    if current_user in giveaway.participants:
        raise HTTPException(status_code=400, detail="Ya estás participando en este giveaway")
    
    # Agregar participante
    giveaway.participants.append(current_user)
    db.commit()
    
    return {
        "success": True,
        "message": "¡Te has inscrito correctamente!",
        "giveaway_id": giveaway.id,
        "joined_at": datetime.utcnow()
    }


# --- Sortear ganador ---
@router.post("/{giveaway_id}/draw", response_model=schemas.GiveawayResponse)
def draw_winner(
    giveaway_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(utils.get_current_user)
):
    giveaway = db.query(models.Giveaway).filter(models.Giveaway.id == giveaway_id).first()
    if not giveaway:
        raise HTTPException(status_code=404, detail="Giveaway no encontrado")
    
    # Solo el creador puede sortear
    if current_user.id != giveaway.creator_id:
        raise HTTPException(status_code=403, detail="Solo el creador puede realizar el sorteo")
    
    # Validaciones
    if giveaway.winner_id:
        raise HTTPException(status_code=400, detail="Este giveaway ya tiene un ganador")
    
    if giveaway.end_date > datetime.utcnow():
        raise HTTPException(status_code=400, detail="El giveaway aún no ha finalizado")
    
    if len(giveaway.participants) == 0:
        raise HTTPException(status_code=400, detail="No hay participantes en este giveaway")
    
    # Sortear ganador aleatoriamente
    from random import choice
    winner = choice(giveaway.participants)
    giveaway.winner_id = winner.id
    giveaway.drawn_at = datetime.utcnow()
    
    db.commit()
    db.refresh(giveaway)
    
    # Enriquecer respuesta
    giveaway.is_owner = True
    giveaway.has_participated = False
    giveaway.can_participate = False
    giveaway.participants_count = len(giveaway.participants)
    
    return giveaway
