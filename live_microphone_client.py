import asyncio
import websockets
import base64
import json
import pyaudio
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("live_microphone_client")

WS_URL = "ws://localhost:10000/ws"
RATE = 8000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 160  # 20ms for 8000Hz

async def stream_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    logger.info("🎤 Starting microphone stream...")

    async with websockets.connect(WS_URL) as ws:
        logger.info("✅ Connected to WebSocket server")
        chunk_id = 0
        try:
            while True:
                audio_chunk = stream.read(CHUNK, exception_on_overflow=False)
                audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
                timestamp = str(int(time.time() * 1000))
                payload = {
                    "event": "media",
                    "media": {
                        "chunk": chunk_id,
                        "timestamp": timestamp,
                        "payload": audio_b64
                    }
                }
                await ws.send(json.dumps(payload))
                chunk_id += 1
                await asyncio.sleep(0.02)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping microphone stream...")
            await ws.send(json.dumps({"event": "stop"}))
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == "__main__":
    asyncio.run(stream_audio())
