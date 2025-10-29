from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True  # ⚠️ Reemplaza orm_mode
    }


class GiveawayBase(BaseModel):
    title: str
    description: str
    prize: str
    image_url: Optional[str] = None
    end_date: datetime


class GiveawayCreate(GiveawayBase):
    pass


class GiveawayResponse(GiveawayBase):
    id: int
    created_at: datetime
    creator: UserResponse
    winner: Optional[UserResponse] = None
    drawn_at: Optional[datetime] = None
    participants_count: int = 0
    has_participated: bool = False  # Se llenará en el endpoint
    can_participate: bool = False   # Se llenará en el endpoint
    is_owner: bool = False         # Se llenará en el endpoint

    model_config = {
        "from_attributes": True
    }


class ParticipateResponse(BaseModel):
    success: bool
    message: str
    giveaway_id: int
    joined_at: datetime
