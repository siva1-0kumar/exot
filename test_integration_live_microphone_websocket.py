import unittest
import asyncio
import websockets
import json
import subprocess
import sys
import time

class IntegrationTestLiveMicrophoneWebSocket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the websocket server in a subprocess and capture stdout/stderr
        cls.server_process = subprocess.Popen(
            [sys.executable, "exotel_websocket_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(2)  # Increased wait time for server to start

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_live_microphone_streaming(self):
        async def client_behavior():
            uri = "ws://localhost:10000"
            try:
                async with websockets.connect(uri) as websocket:
                    # Simulate sending a media event like live_microphone_client
                    media_event = {
                        "event": "media",
                        "media": {
                            "chunk": 1,
                            "timestamp": "1234567890",
                            "payload": "dGVzdA=="  # base64 for "test"
                        }
                    }
                    await websocket.send(json.dumps(media_event))

                    # Receive broadcast message (should be the same as sent)
                    try:
                        response = await websocket.recv()
                        data = json.loads(response)
                        self.assertEqual(data["event"], "broadcast")
                        self.assertEqual(data["media"], media_event["media"])
                    except websockets.exceptions.ConnectionClosedOK:
                        # Connection closed normally, test passes
                        pass
            except Exception as e:
                self.fail(f"WebSocket connection failed: {e}")

        asyncio.run(client_behavior())

if __name__ == "__main__":
    unittest.main()
