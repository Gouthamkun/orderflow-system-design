from pydantic import BaseModel


class OrderCreate(BaseModel):
    user_id: int
    restaurant: str
    items: str


class OrderUpdate(BaseModel):
    status: str


class OrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant: str
    items: str
    status: str

    class Config:
        from_attributes = True