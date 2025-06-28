import unittest
import asyncio
import websockets
import json
from threading import Thread
import time

import exotel_websocket_server

class WebSocketServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the websocket server in a separate thread
        cls.loop = asyncio.new_event_loop()
        cls.server_thread = Thread(target=cls.start_server, args=(cls.loop,), daemon=True)
        cls.server_thread.start()
        time.sleep(1)  # Wait for server to start

    @classmethod
    def start_server(cls, loop):
        import asyncio
        import subprocess
        import sys
        # Start the server in a subprocess to avoid event loop conflicts
        cls.server_process = subprocess.Popen([sys.executable, "exotel_websocket_server.py"])
        # Wait a bit for the server to start
        import time
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_client_connection_and_broadcast(self):
        async def client_behavior():
            uri = "ws://localhost:10000/ws"
            async with websockets.connect(uri) as websocket1, websockets.connect(uri) as websocket2:
                # websocket1 sends a media event
                media_event = {
                    "event": "media",
                    "media": {
                        "chunk": 1,
                        "timestamp": "1234567890",
                        "payload": "testpayload"
                    }
                }
                await websocket1.send(json.dumps(media_event))

                # websocket2 should receive the broadcast
                response = await websocket2.recv()
                data = json.loads(response)
                self.assertEqual(data["event"], "broadcast")
                self.assertEqual(data["media"], media_event["media"])

        import asyncio
        asyncio.run(client_behavior())

if __name__ == "__main__":
    unittest.main()
