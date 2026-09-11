import asyncio
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect
)
from app.pubsub import publish_order_update
from app.connection_manager import manager
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from app.payment_client import make_payment
from app.kafka_client import producer
from app.redis_client import redis_client
from app.database import SessionLocal
from app.models import Order
from fastapi import WebSocket, WebSocketDisconnect

from app.schemas import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    PaymentWebhook
)
from app.rate_limiter import check_rate_limit
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Rate limiting
    if not check_rate_limit(order.user_id):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    new_order = Order(
        user_id=order.user_id,
        restaurant=order.restaurant,
        items=order.items,
        status="PLACED"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    payment = make_payment(new_order.id, 499.0)

    if not payment.success:
        new_order.status = "PAYMENT_FAILED"
        db.commit()
    event = {
    "order_id": new_order.id,
    "event": "ORDER_CREATED"
  }

    producer.send("orders", value=event)
    producer.flush()

    return new_order
@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):

    # 1. Check Redis
    cached_order = redis_client.get(f"order:{order_id}")

    if cached_order:
        print("CACHE HIT")
        return json.loads(cached_order)

    # 2. Cache miss → check PostgreSQL
    print("CACHE MISS")

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 3. Store order in Redis
    order_data = {
        "id": order.id,
        "user_id": order.user_id,
        "restaurant": order.restaurant,
        "items": order.items,
        "status": order.status
    }

    redis_client.set(
        f"order:{order_id}",
        json.dumps(order_data),
        ex=300
    )

    return order_data
@router.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = order_update.status

    db.commit()
    db.refresh(order)

    # Invalidate cached order
    redis_client.delete(f"order:{order_id}")

    # Notify connected WebSocket clients
    publish_order_update(order_id, order.status)

    return order


@router.websocket("/ws/orders/{order_id}")
async def order_websocket(websocket: WebSocket, order_id: int):
    await manager.connect(order_id, websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(order_id, websocket)
        print(f"Client disconnected from order {order_id}")
@router.post("/test-broadcast/{order_id}")
async def test_broadcast(order_id: int):

    await manager.broadcast(
        order_id,
        {
            "order_id": order_id,
            "status": "PREPARING"
        }
    )

    return {
        "message": "Broadcast sent",
        "order_id": order_id
    }
@router.post("/webhooks/payment")
async def payment_webhook(
    webhook: PaymentWebhook,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == webhook.order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if webhook.status == "SUCCESS":
        order.status = "PAID"

    elif webhook.status == "FAILED":
        order.status = "PAYMENT_FAILED"

    db.commit()
    db.refresh(order)

    redis_client.delete(
        f"order:{order.id}"
    )

    publish_order_update(
        order.id,
        order.status
    )

    return {
        "message": "Webhook processed",
        "order_id": order.id,
        "status": order.status
    }