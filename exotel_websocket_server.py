import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("exotel_websocket_server")

connected_clients = set()

async def handler(websocket):
    # Removed path check due to incompatibility with websockets version
    # Accept all connections

    # Register client
    connected_clients.add(websocket)
    logger.info(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            # Parse JSON message
            try:
                data = json.loads(message)
                event = data.get("event")
                if event == "media":
                    # Broadcast media event to all other clients
                    broadcast_message = json.dumps({
                        "event": "broadcast",
                        "media": data.get("media")
                    })
                    await asyncio.gather(*[asyncio.create_task(client.send(broadcast_message)) for client in connected_clients if client != websocket])
                    logger.info(f"Broadcasted media event from {websocket.remote_address}")
                elif event == "stop":
                    # Handle stop event if needed
                    logger.info(f"Received stop event from {websocket.remote_address}")
                    pass
            except json.JSONDecodeError:
                # Ignore non-JSON messages
                logger.warning(f"Received non-JSON message from {websocket.remote_address}")
                pass
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {websocket.remote_address}")
    finally:
        # Unregister client
        connected_clients.remove(websocket)
        logger.info(f"Client removed: {websocket.remote_address}")

async def main():
    server = await websockets.serve(handler, "localhost", 10000)
    logger.info("WebSocket server started on ws://localhost:10000/ws")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
