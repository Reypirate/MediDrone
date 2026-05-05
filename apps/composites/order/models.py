from datetime import datetime
from sqlmodel import Field, SQLModel


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: str = Field(index=True, unique=True)
    hospital_id: str | None = None
    hospital_name: str | None = None
    item_id: str
    quantity: int = 1
    urgency_level: str = "NORMAL"
    customer_address: str | None = ""
    customer_lat: float
    customer_lng: float
    status: str = "PENDING"
    mission_phase: str | None = None
    drone_id: str | None = None
    eta_minutes: float | None = None
    dispatch_status: str | None = None
    route_id: str | None = None
    updated_eta: str | None = None
    reroute_details: str | None = None  # JSON string
    cancel_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
