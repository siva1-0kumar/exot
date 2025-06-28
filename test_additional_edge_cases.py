import unittest
import asyncio
import websockets
import json

class AdditionalEdgeCasesTest(unittest.TestCase):
    async def send_invalid_json(self, websocket):
        await websocket.send("Invalid JSON")

    async def send_unknown_event(self, websocket):
        await websocket.send(json.dumps({"event": "unknown"}))

    async def send_stop_event(self, websocket):
        await websocket.send(json.dumps({"event": "stop"}))

    def test_invalid_json_handling(self):
        async def test():
            uri = "ws://localhost:10000"
            async with websockets.connect(uri) as websocket:
                await self.send_invalid_json(websocket)
                # No exception should be raised, server should ignore invalid JSON
                await self.send_stop_event(websocket)
        asyncio.run(test())

    def test_unknown_event_handling(self):
        async def test():
            uri = "ws://localhost:10000"
            async with websockets.connect(uri) as websocket:
                await self.send_unknown_event(websocket)
                # No exception should be raised, server should ignore unknown event
                await self.send_stop_event(websocket)
        asyncio.run(test())

if __name__ == "__main__":
    unittest.main()
