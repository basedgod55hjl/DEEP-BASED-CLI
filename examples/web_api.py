#!/usr/bin/env python3
"""
FastAPI Web Service for DeepSeek API

This example creates a REST API that exposes DeepSeek functionality including:
- Chat completions endpoint
- Reasoning endpoint
- Function calling
- Streaming responses
- WebSocket support for real-time chat
"""

import sys
import json
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add parent directory to path
sys.path.append('..')
from deepseek_integration import DeepSeekClient, DeepSeekModel, ResponseFormat


# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation messages")
    model: Optional[str] = Field("deepseek-chat", description="Model to use")
    temperature: Optional[float] = Field(0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    response_format: Optional[str] = Field(None, description="Response format: 'json' or None")


class ReasoningRequest(BaseModel):
    prompt: str = Field(..., description="Problem or question to solve")
    reasoning_effort: Optional[str] = Field("medium", description="Reasoning effort: low, medium, high")
    show_reasoning: Optional[bool] = Field(True, description="Include reasoning steps")


class FunctionDefinition(BaseModel):
    name: str = Field(..., description="Function name")
    description: str = Field(..., description="Function description")
    parameters: Dict[str, Any] = Field(..., description="Function parameters (JSON Schema)")
    required: Optional[List[str]] = Field([], description="Required parameter names")


class FunctionCallRequest(BaseModel):
    messages: List[ChatMessage]
    functions: List[FunctionDefinition]
    function_call: Optional[str] = Field("auto", description="Function calling mode")


class BatchRequest(BaseModel):
    prompts: List[str] = Field(..., description="List of prompts to process")
    model: Optional[str] = Field("deepseek-chat", description="Model to use")
    max_concurrent: Optional[int] = Field(5, description="Maximum concurrent requests")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")


# Global client instance
deepseek_client: Optional[DeepSeekClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global deepseek_client
    # Startup
    deepseek_client = DeepSeekClient()
    print("DeepSeek client initialized")
    yield
    # Shutdown
    if deepseek_client:
        usage = deepseek_client.get_usage_summary()
        print(f"Total usage: {usage}")


# Create FastAPI app
app = FastAPI(
    title="DeepSeek API Service",
    description="REST API wrapper for DeepSeek language models",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "DeepSeek API Service",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/v1/chat",
            "reasoning": "/api/v1/reason",
            "functions": "/api/v1/functions/call",
            "batch": "/api/v1/batch",
            "usage": "/api/v1/usage",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "client_active": deepseek_client is not None
    }


@app.post("/api/v1/chat")
async def chat_completion(request: ChatRequest):
    """
    Chat completion endpoint
    
    Supports both streaming and non-streaming responses
    """
    if not deepseek_client:
        raise HTTPException(status_code=500, detail="DeepSeek client not initialized")
    
    try:
        # Convert messages to dict format
        messages = [msg.dict() for msg in request.messages]
        
        # Determine model
        model = DeepSeekModel.CHAT if request.model == "deepseek-chat" else DeepSeekModel.REASONER
        
        # Determine response format
        response_format = None
        if request.response_format == "json":
            response_format = ResponseFormat.JSON
        
        if request.stream:
            # Streaming response
            async def generate():
                stream = await deepseek_client.achat(
                    messages=messages,
                    model=model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=True,
                    response_format=response_format
                )
                async for chunk in stream:
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            # Non-streaming response
            response = await deepseek_client.achat(
                messages=messages,
                model=model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                response_format=response_format
            )
            
            return {
                "response": response,
                "model": model.value,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/reason")
async def reasoning_endpoint(request: ReasoningRequest):
    """
    Reasoning endpoint for complex problem-solving
    """
    if not deepseek_client:
        raise HTTPException(status_code=500, detail="DeepSeek client not initialized")
    
    try:
        result = deepseek_client.reason(
            prompt=request.prompt,
            reasoning_effort=request.reasoning_effort,
            show_reasoning=request.show_reasoning
        )
        
        return {
            "answer": result["answer"],
            "reasoning": result.get("reasoning", ""),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/functions/call")
async def function_calling(request: FunctionCallRequest):
    """
    Function calling endpoint
    """
    if not deepseek_client:
        raise HTTPException(status_code=500, detail="DeepSeek client not initialized")
    
    try:
        # Convert messages
        messages = [msg.dict() for msg in request.messages]
        
        # Create tool definitions
        tools = []
        for func in request.functions:
            tool = deepseek_client.create_function_tool(
                name=func.name,
                description=func.description,
                parameters=func.parameters,
                required=func.required
            )
            tools.append(tool)
        
        # Make request
        response = await deepseek_client.achat(
            messages=messages,
            tools=tools,
            tool_choice=request.function_call
        )
        
        return {
            "function_calls": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch")
async def batch_processing(request: BatchRequest):
    """
    Batch processing endpoint for multiple prompts
    """
    if not deepseek_client:
        raise HTTPException(status_code=500, detail="DeepSeek client not initialized")
    
    try:
        model = DeepSeekModel.CHAT if request.model == "deepseek-chat" else DeepSeekModel.REASONER
        
        # Process batch
        responses = []
        semaphore = asyncio.Semaphore(request.max_concurrent)
        
        async def process_one(prompt: str) -> Dict[str, str]:
            async with semaphore:
                response = await deepseek_client.achat(
                    prompt,
                    model=model,
                    temperature=request.temperature
                )
                return {"prompt": prompt, "response": response}
        
        tasks = [process_one(prompt) for prompt in request.prompts]
        responses = await asyncio.gather(*tasks)
        
        return {
            "results": responses,
            "count": len(responses),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/usage")
async def get_usage():
    """
    Get usage statistics
    """
    if not deepseek_client:
        raise HTTPException(status_code=500, detail="DeepSeek client not initialized")
    
    usage = deepseek_client.get_usage_summary()
    return usage


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat
    """
    await websocket.accept()
    
    if not deepseek_client:
        await websocket.send_json({"error": "DeepSeek client not initialized"})
        await websocket.close()
        return
    
    conversation_history = []
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "chat":
                # Add user message to history
                user_message = {"role": "user", "content": data["message"]}
                conversation_history.append(user_message)
                
                # Keep last 10 messages for context
                context_messages = conversation_history[-10:]
                
                # Stream response
                stream = await deepseek_client.achat(
                    messages=context_messages,
                    stream=True,
                    temperature=data.get("temperature", 0.7)
                )
                
                full_response = ""
                async for chunk in stream:
                    await websocket.send_json({
                        "type": "stream",
                        "content": chunk
                    })
                    full_response += chunk
                
                # Add assistant response to history
                conversation_history.append({
                    "role": "assistant",
                    "content": full_response
                })
                
                # Send completion signal
                await websocket.send_json({
                    "type": "complete",
                    "message": full_response
                })
                
            elif data.get("type") == "clear":
                conversation_history.clear()
                await websocket.send_json({
                    "type": "cleared",
                    "message": "Conversation history cleared"
                })
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()


# Example HTML client for testing WebSocket
@app.get("/ws-test", response_class=JSONResponse)
async def websocket_test_page():
    """Return a simple HTML page for testing WebSocket"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DeepSeek WebSocket Test</title>
    </head>
    <body>
        <h1>DeepSeek Chat WebSocket Test</h1>
        <div id="messages" style="border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px;"></div>
        <input type="text" id="messageInput" style="width: 80%;" placeholder="Type your message...">
        <button onclick="sendMessage()">Send</button>
        <button onclick="clearChat()">Clear</button>
        
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws/chat");
            const messagesDiv = document.getElementById("messages");
            const messageInput = document.getElementById("messageInput");
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === "stream") {
                    // Append streaming content
                    const lastMessage = messagesDiv.lastElementChild;
                    if (lastMessage && lastMessage.className === "assistant-streaming") {
                        lastMessage.textContent += data.content;
                    } else {
                        const div = document.createElement("div");
                        div.className = "assistant-streaming";
                        div.textContent = "Assistant: " + data.content;
                        messagesDiv.appendChild(div);
                    }
                } else if (data.type === "complete") {
                    // Mark message as complete
                    const lastMessage = messagesDiv.lastElementChild;
                    if (lastMessage && lastMessage.className === "assistant-streaming") {
                        lastMessage.className = "assistant";
                    }
                }
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            };
            
            function sendMessage() {
                const message = messageInput.value;
                if (message) {
                    const div = document.createElement("div");
                    div.textContent = "You: " + message;
                    messagesDiv.appendChild(div);
                    
                    ws.send(JSON.stringify({
                        type: "chat",
                        message: message
                    }));
                    
                    messageInput.value = "";
                }
            }
            
            function clearChat() {
                ws.send(JSON.stringify({type: "clear"}));
                messagesDiv.innerHTML = "";
            }
            
            messageInput.addEventListener("keypress", function(e) {
                if (e.key === "Enter") {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return JSONResponse(content={"html": html_content})


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "web_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )