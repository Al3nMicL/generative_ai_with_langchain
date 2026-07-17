import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

MODULE_PATH = Path(__file__).resolve().parents[1] / "main.py"


def load_main(module_name: str = "chapter9_fastapi_main_test"):
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class FakeChain:
    def __init__(self, *, response: str = "ok", chunks=None):
        self.response = response
        self.chunks = chunks or []
        self.ainvoke_calls = []
        self.astream_calls = []

    async def ainvoke(self, payload):
        self.ainvoke_calls.append(payload)
        return self.response

    async def astream(self, payload):
        self.astream_calls.append(payload)
        for chunk in self.chunks:
            yield chunk


class FastAPIMainTests(unittest.TestCase):
    def setUp(self):
        self.module = load_main(f"chapter9_fastapi_main_test_{id(self)}")

    def tearDown(self):
        sys.modules.pop(self.module.__name__, None)

    def test_root_route_serves_chat_ui(self):
        with TestClient(self.module.app) as client:
            response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Chatbot Playground", response.text)

    def test_chat_accepts_message_field(self):
        fake_chain = FakeChain(response="hello")

        with patch.object(self.module, "build_chain", return_value=fake_chain):
            with TestClient(self.module.app) as client:
                response = client.post("/chat", json={"message": "hi"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "hello"})
        self.assertEqual(
            fake_chain.ainvoke_calls[0]["messages"][0].content,
            "hi",
        )

    def test_chat_accepts_input_alias(self):
        fake_chain = FakeChain(response="alias-ok")

        with patch.object(self.module, "build_chain", return_value=fake_chain):
            with TestClient(self.module.app) as client:
                response = client.post("/chat", json={"input": "legacy"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "alias-ok"})
        self.assertEqual(
            fake_chain.ainvoke_calls[0]["messages"][0].content,
            "legacy",
        )

    def test_stream_route_uses_sse_framing(self):
        fake_chain = FakeChain(chunks=["hello", " world"])

        with patch.object(self.module, "build_chain", return_value=fake_chain):
            with TestClient(self.module.app) as client:
                response = client.post("/chat/stream", json={"message": "hi"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("text/event-stream"))
        self.assertIn("data: hello\n\n", response.text)
        self.assertIn("data:  world\n\n", response.text)
        self.assertIn("event: end\ndata: [DONE]\n\n", response.text)
        self.assertEqual(len(fake_chain.ainvoke_calls), 0)
        self.assertEqual(len(fake_chain.astream_calls), 1)

    def test_websocket_streams_json_events_from_astream_only(self):
        fake_chain = FakeChain(chunks=["hel", "lo"])

        with patch.object(self.module, "build_chain", return_value=fake_chain):
            with TestClient(self.module.app) as client:
                with client.websocket_connect("/ws") as websocket:
                    websocket.send_text("hi")
                    self.assertEqual(
                        websocket.receive_json(),
                        {"sender": "bot", "message_type": "start"},
                    )
                    self.assertEqual(
                        websocket.receive_json(),
                        {"sender": "bot", "message_type": "stream", "message": "hel"},
                    )
                    self.assertEqual(
                        websocket.receive_json(),
                        {"sender": "bot", "message_type": "stream", "message": "lo"},
                    )
                    self.assertEqual(
                        websocket.receive_json(),
                        {"sender": "bot", "message_type": "end"},
                    )

        self.assertEqual(len(fake_chain.ainvoke_calls), 0)
        self.assertEqual(len(fake_chain.astream_calls), 1)


class EnvironmentLoadingTests(unittest.TestCase):
    def test_module_loads_dotenv_on_import(self):
        module_name = "chapter9_fastapi_main_env_test"
        sys.modules.pop(module_name, None)

        with patch("dotenv.load_dotenv") as mock_load_dotenv:
            module = load_main(module_name)

        self.assertTrue(mock_load_dotenv.called)
        sys.modules.pop(module.__name__, None)
