import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from app.main import app, get_ai_suggestions
import json

client = TestClient(app)

@pytest.fixture(scope="function")
async def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text  # Ensure HTML is returned


@pytest.mark.asyncio
async def test_ai_suggestions():
    code_snippet = "print('Hello, world!')"
    suggestion = await get_ai_suggestions(code_snippet)
    assert isinstance(suggestion, str)  # Should return a string
    assert "AI Error" not in suggestion  # Should not return an error message


@pytest.mark.asyncio
async def test_websocket_connection():
    doc_id = "test_doc"
    with client.websocket_connect(f"/ws/{doc_id}") as websocket:
        websocket.send_text(json.dumps({"type": "code", "content": "print('Hello')"}))
        response = websocket.receive_text()
        response_data = json.loads(response)
        assert response_data["type"] == "code"
        assert "print('Hello')" in response_data["content"]


@pytest.mark.asyncio
async def test_websocket_ai_suggestion():
    doc_id = "test_ai"
    with client.websocket_connect(f"/ws/{doc_id}") as websocket:
        websocket.send_text(json.dumps({"type": "code", "content": "# What is the output of this function?"}))
        response = websocket.receive_text()
        response_data = json.loads(response)
        assert response_data["type"] == "code"
        assert "# AI Suggestion:" in response_data["content"]


@pytest.mark.asyncio
async def test_execute_code():
    response = client.post("/execute", json={"doc_id": "test_doc", "code": "print('Hello, world!')"})
    assert response.status_code == 200
    assert response.json()["output"].strip() == "Hello, world!"
