from sqlalchemy import Column, Integer, String
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    restaurant = Column(String, nullable=False)
    items = Column(String, nullable=False)
    status = Column(String, default="PLACED")