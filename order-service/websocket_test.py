import asyncio
import websockets


async def client(name):
    uri = "ws://127.0.0.1:8001/ws/orders/25"

    async with websockets.connect(uri) as websocket:
        print(f"{name} connected")

        try:
            while True:
                message = await websocket.recv()
                print(f"{name} received:", message)

        except websockets.exceptions.ConnectionClosed:
            print(f"{name} disconnected")


async def main():
    await asyncio.gather(
        client("Client A"),
        client("Client B")
    )


asyncio.run(main())