from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import requests
import sys
import io
from typing import Dict, List
import re
from app.config import HF_API_KEY, API_URL


app = FastAPI()

active_connections: Dict[str, List[WebSocket]] = {}

code_snippets: Dict[str, str] = {}

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

@app.get("/", response_class=HTMLResponse)
async def get():
    """Serve the frontend HTML."""
    with open("index.html", "r") as file:
        return file.read()


async def get_ai_suggestions(code_snippet):
    """Fetch AI suggestions from Hugging Face StarCoder."""
    payload = {
        "inputs": code_snippet,
        "parameters": {"max_new_tokens": 50, "temperature": 0.2}
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response_data = response.json()
        print(response_data)
        if isinstance(response_data, list) and "generated_text" in response_data[0]:
            suggestion = response_data[0]["generated_text"]
            print("suggestion",suggestion)
            matches = re.findall(r"# (.*?)#", suggestion, re.DOTALL)
            print("matches",matches)
            return matches[0].strip() if matches else print("Error")
        else:
            return "AI Error: No valid suggestion"
    except Exception as e:
        return f"AI Error: {str(e)}"



@app.websocket("/ws/{doc_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: str):
    """WebSocket for real-time collaboration and AI suggestions."""
    await websocket.accept()

    if doc_id not in active_connections:
        active_connections[doc_id] = []
    active_connections[doc_id].append(websocket)

    if doc_id in code_snippets:
        await websocket.send_text(json.dumps({"type": "code", "content": code_snippets[doc_id]}))

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)

            if data["type"] == "code":
                code_snippets[doc_id] = data["content"]

                last_line = data["content"].strip().split("\n")[-1].strip()
                if last_line.startswith("#"):
                    ai_suggestion = await get_ai_suggestions(data["content"])
                    
                    if "AI Error" not in ai_suggestion and ai_suggestion not in data["content"]:
                        response = json.dumps({"type": "code", "content": f"\n# AI Suggestion:\n{ai_suggestion}"})
                        await websocket.send_text(response)

                for connection in active_connections[doc_id]:
                    if connection != websocket:
                        await connection.send_text(json.dumps({"type": "code", "content": data["content"]}))

    except WebSocketDisconnect:
        active_connections[doc_id].remove(websocket)
        if not active_connections[doc_id]:
            del active_connections[doc_id]


class CodeExecutionRequest(BaseModel):
    doc_id: str
    code: str


@app.post("/execute")
async def execute_code(request: CodeExecutionRequest):
    """Execute Python code and return output."""
    try:
        old_stdout = sys.stdout
        sys.stdout = new_stdout = io.StringIO()

        exec(request.code, {}, {})  

        output = new_stdout.getvalue()
        sys.stdout = old_stdout 

        if request.doc_id in active_connections:
            for conn in active_connections[request.doc_id]:
                await conn.send_text(json.dumps({"type": "output", "content": output}))

        return {"output": output}
    except Exception as e:
        sys.stdout = old_stdout 
        return {"output": str(e)}
