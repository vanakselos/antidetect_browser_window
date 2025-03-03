from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import sys
import os
import json
import uvicorn
import asyncio
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Import existing components
from src.core.browser_manager import BrowserManager
from src.core.profile_manager import ProfileManager
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Data models
class Position(BaseModel):
    x: float
    y: float


class NodeData(BaseModel):
    label: str
    type: str
    config: Optional[Dict[str, Any]] = None


class Node(BaseModel):
    id: str
    type: str
    position: Position
    data: NodeData


class Edge(BaseModel):
    id: str
    source: str
    target: str


class Workflow(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


class Profile(BaseModel):
    name: str
    fingerprint: Optional[Dict[str, Any]] = None


class WorkflowSuggestionRequest(BaseModel):
    command: str


# WebSocket manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)


# Initialize FastAPI app
app = FastAPI(title="Browser Automation API")
manager = ConnectionManager()
logger = setup_logger()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
browser_manager = BrowserManager()
profile_manager = ProfileManager()



# Profile management endpoints
@app.get("/api/profiles")
async def get_profiles():
    """Get all available profiles"""
    try:
        profiles = profile_manager.get_all_profiles()
        return {
            "profiles": [
                {
                    "name": name,
                    "fingerprint": profile.fingerprint,
                    "created_at": datetime.now().isoformat()  # Add creation date in real implementation
                }
                for name, profile in profiles.items()
            ]
        }
    except Exception as e:
        logger.error(f"Error getting profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/profiles")
async def create_profile(profile: Profile):
    """Create a new browser profile"""
    try:
        if profile_manager.create_profile(profile.name):
            await manager.broadcast(f"Profile created: {profile.name}")
            return {"message": f"Profile {profile.name} created successfully"}
        raise HTTPException(status_code=400, detail="Profile creation failed")
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/profiles/{profile_name}")
async def delete_profile(profile_name: str):
    """Delete a browser profile"""
    try:
        # Implement profile deletion
        return {"message": f"Profile {profile_name} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Browser control endpoints
@app.post("/api/browser/launch/{profile_name}")
async def launch_browser(profile_name: str):
    """Launch browser with specified profile"""
    try:
        if browser_manager.launch_profile(profile_name):
            await manager.broadcast(f"Browser launched for profile: {profile_name}")
            return {"message": "Browser launched successfully"}
        raise HTTPException(status_code=400, detail="Failed to launch browser")
    except Exception as e:
        logger.error(f"Error launching browser: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Workflow management endpoints
@app.post("/api/workflows/execute")
async def execute_workflow(workflow: Workflow):
    """Execute a workflows"""
    try:
        # Validate workflows
        if not workflow.nodes:
            raise HTTPException(status_code=400, detail="Workflow must have at least one node")

        # Find start node
        start_node = next((node for node in workflow.nodes if node.type == "trigger"), None)
        if not start_node:
            raise HTTPException(status_code=400, detail="Workflow must have a trigger node")

        # Execute workflows (implement actual execution logic)
        await manager.broadcast("Workflow execution started")

        # Simulate workflows execution (replace with actual implementation)
        for node in workflow.nodes:
            await asyncio.sleep(1)  # Simulate processing time
            await manager.broadcast(f"Executing node: {node.id}")

        return {"message": "Workflow executed successfully"}
    except Exception as e:
        logger.error(f"Error executing workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflows/nodes")
async def get_available_nodes():
    """Get available node types"""
    return {
        "nodes": [
            {
                "type": "trigger",
                "title": "Schedule Trigger",
                "description": "Trigger workflows on schedule",
                "category": "Triggers",
                "inputs": [],
                "outputs": ["next"]
            },
            {
                "type": "http",
                "title": "HTTP Request",
                "description": "Make HTTP requests",
                "category": "Actions",
                "inputs": ["trigger"],
                "outputs": ["next"]
            },
            {
                "type": "code",
                "title": "Code",
                "description": "Execute custom code",
                "category": "Actions",
                "inputs": ["input"],
                "outputs": ["output"]
            }
        ]
    }


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )


# New endpoint
@app.post("/api/workflow/suggest")
async def suggest_workflow(request: WorkflowSuggestionRequest):
    """Generate workflow suggestion based on user command"""
    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a workflow automation expert. Convert user commands into workflow nodes and connections.
                    Available node types: navigate, click, type, openai, wait, condition, loop.
                    Return JSON format: { 
                        "nodes": [{"type": "string", "title": "string", "config": {}}], 
                        "connections": [{"sourceIndex": number, "targetIndex": number}]
                    }"""
                },
                {
                    "role": "user",
                    "content": request.command
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Parse and validate the response
        suggestion = json.loads(completion.choices[0].message.content)
        return suggestion

    except Exception as e:
        logger.error(f"Error generating workflow suggestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Main entry point
if __name__ == "__main__":
    try:
        # Create necessary directories
        for directory in ['logs', 'profiles']:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Run the FastAPI application
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

