from sqlmodel import Field, SQLModel


class Inventory(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    hospital_id: str = Field(primary_key=True)
    item_id: str = Field(primary_key=True)
    name: str
    quantity: int
