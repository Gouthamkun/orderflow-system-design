from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI(title="OrderFlow API Gateway")

ORDER_SERVICES = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
]

current_server = 0


def get_next_server():
    global current_server

    server = ORDER_SERVICES[current_server]
    current_server = (current_server + 1) % len(ORDER_SERVICES)

    return server


@app.api_route(
    "/orders",
    methods=["GET", "POST"]
)
def orders(request: Request):

    server = get_next_server()

    try:
        response = requests.request(
            method=request.method,
            url=f"{server}/orders",
            json=None if request.method == "GET" else {},
        )

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

    except requests.RequestException:
        return JSONResponse(
            status_code=503,
            content={"detail": "Order Service unavailable"}
        )


@app.get("/orders/{order_id}")
def get_order(order_id: int):

    server = get_next_server()

    try:
        response = requests.get(
            f"{server}/orders/{order_id}"
        )

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

    except requests.RequestException:
        return JSONResponse(
            status_code=503,
            content={"detail": "Order Service unavailable"}
        )


@app.get("/health")
def health():
    return {
        "gateway": "healthy",
        "services": ORDER_SERVICES
    }