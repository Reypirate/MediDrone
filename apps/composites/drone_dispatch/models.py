from datetime import datetime
from sqlmodel import Field, SQLModel


class Mission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: str = Field(index=True, unique=True)
    drone_id: str
    status: str = "TO_HOSPITAL"
    current_lat: float
    current_lng: float
    target_lat: float
    target_lng: float
    eta_minutes: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
