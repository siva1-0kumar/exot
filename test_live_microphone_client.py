import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
import base64
import json
import time

import importlib.util
import sys
import os

import live_microphone_client as lmc

class TestLiveMicrophoneClient(unittest.IsolatedAsyncioTestCase):
    @patch('live_microphone_client.pyaudio.PyAudio')
    @patch('live_microphone_client.websockets.connect')
    async def test_stream_audio_sends_payloads(self, mock_ws_connect, mock_pyaudio):
        # Setup mocks
        mock_stream = MagicMock()
        mock_stream.read.return_value = b'audiochunk'
        mock_pyaudio.return_value.open.return_value = mock_stream

        mock_ws = AsyncMock()
        mock_ws_connect.return_value.__aenter__.return_value = mock_ws

        # Run the coroutine for a few iterations then cancel
        async def run_stream():
            task = asyncio.create_task(lmc.stream_audio())
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        await run_stream()

        # Check that websocket connect was called with correct URL
        mock_ws_connect.assert_called_with(lmc.WS_URL)

        # Check that send was called with JSON payloads containing expected keys
        send_calls = mock_ws.send.call_args_list
        self.assertTrue(len(send_calls) > 0)
        for call in send_calls:
            arg = call.args[0]
            data = json.loads(arg)
            self.assertIn('event', data)
            if data['event'] == 'media':
                self.assertIn('media', data)
                self.assertIn('chunk', data['media'])
                self.assertIn('timestamp', data['media'])
                self.assertIn('payload', data['media'])
                # Check payload is base64 string
                base64.b64decode(data['media']['payload'])

    @patch('live_microphone_client.pyaudio.PyAudio')
    @patch('live_microphone_client.websockets.connect')
    async def test_keyboard_interrupt_stops_stream(self, mock_ws_connect, mock_pyaudio):
        mock_stream = MagicMock()
        mock_stream.read.return_value = b'audiochunk'
        mock_pyaudio.return_value.open.return_value = mock_stream

        mock_ws = AsyncMock()
        mock_ws_connect.return_value.__aenter__.return_value = mock_ws

        # Patch print to suppress output during test
        with patch('builtins.print'):
            # Simulate KeyboardInterrupt after a few sends
            original_read = mock_stream.read
            call_count = 0

            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count > 3:
                    raise KeyboardInterrupt()
                return original_read()

            mock_stream.read.side_effect = side_effect

            await lmc.stream_audio()

        # Check that stop event was sent
        stop_event = json.dumps({"event": "stop"})
        mock_ws.send.assert_any_call(stop_event)
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        mock_pyaudio.return_value.terminate.assert_called_once()

if __name__ == '__main__':
    unittest.main()
