## Real-Time Collaborative Code Editor with AI Suggestions

## Overview
This project is a real-time collaborative code editor that allows multiple users to edit the same code file simultaneously. It integrates an AI model (Hugging Face StarCoder) to provide real-time code suggestions and debugging assistance.

## Features
- Real-time Collaboration: Multiple users can edit the same document simultaneously.
- AI-Powered Suggestions: Uses an LLM model to suggest code improvements and explanations.
- WebSockets for Live Updates: Implements FastAPI WebSockets to handle live data transfer.
- Code Execution: Supports execution of Python code within the editor.

## Technologies Used
- Backend: FastAPI, WebSockets, Pydantic
- Frontend: HTML, JavaScript
- AI Model: Hugging Face StarCoder API
- Testing: Pytest, pytest-asyncio

### Prerequisites
- Python 3.10+
- pip

### Steps to Run
1. Install dependencies:
 
   pip install -r requirements.txt

2. Set up environment variables:

   export HF_API_KEY=api_key
   export API_URL=https://api-inference.huggingface.co/models/bigcode/starcoder

3. Run the application:

   uvicorn app.main:app --reload

4. Open the editor in the browser:

   http://localhost:8000

## Running Tests
To execute the test suite, run:

pytest tests --asyncio-mode=auto

## API Endpoints

### 1. Serve Frontend

GET /
Returns the HTML frontend.

### 2. WebSocket Endpoint

ws://localhost:8000/ws/{doc_id}
Handles real-time collaboration.

### 3. Execute Code

POST /execute
Executes the provided Python code and returns output.
