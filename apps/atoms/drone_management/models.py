from sqlmodel import Field, SQLModel


class Drone(SQLModel, table=True):
    drone_id: str = Field(primary_key=True)
    battery: int
    status: str
    lat: float
    lng: float
    current_lat: float | None = None
    current_lng: float | None = None
    target_lat: float | None = None
    target_lng: float | None = None
