import websockets
import os
import json

async def send_websocket_message(message):
    async with websockets.connect(os.environ.get("WEBSOCKET_URL")) as websocket:
        try:
            message["client_type"] = "backend"
            await websocket.send(json.dumps(message))
        except Exception as e:
            print("Error sending WebSocket message:", e)
        finally:
            await websocket.close()
