from typing import Optional, Annotated
from fastapi import (
    Cookie,
    Depends,
    Query,
    WebSocketException,
    WebSocketDisconnect,
    status
)
from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse

router =  APIRouter()

def get_html(channel_id: str):
    return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Chat</title>
            </head>
            <body>
                <h1>WebSocket Chat for Channel: {channel_id}</h1>
                <h2>Your ID: <span id="ws-id"></span></h2>
                <form action="" onsubmit="sendMessage(event)">
                    <input type="text" id="messageText" autocomplete="off"/>
                    <button>Send</button>
                </form>
                <ul id='messages'>
                </ul>
                <script>
                    const client_id = Date.now();
                    const channel_id = "{channel_id}"; // Get channel_id from Python
                    document.querySelector("#ws-id").textContent = client_id;
                    
                    // CHANGED: Correct WebSocket URL format
                    const ws = new WebSocket(`ws://localhost:8000/websocket/ws/${{channel_id}}/${{client_id}}`);
                    
                    ws.onmessage = function(event) {{
                        const messages = document.getElementById('messages');
                        const message = document.createElement('li');
                        const content = document.createTextNode(event.data);
                        message.appendChild(content);
                        messages.appendChild(message);
                    }};
                    
                    function sendMessage(event) {{
                        const input = document.getElementById("messageText");
                        // CHANGED: ws.send() only takes one argument
                        ws.send(input.value);
                        input.value = '';
                        event.preventDefault();
                    }}
                </script>
            </body>
        </html>
        """

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, list[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, channel_id: str):
        await websocket.accept()
        connections = self.active_connections
        if connections.get(channel_id):
            connections[channel_id].append(websocket)
        else:
            connections[channel_id] = [websocket]
        count = self.connection_count(channel_id)
        ws_channel = connections[channel_id]
        for ws in ws_channel:
            await ws.send_text(f"Connection count: {count}")
        
    def connection_count(self, channel_id: str):
        connection = self.active_connections
        if connection.get(channel_id):
            return len(connection[channel_id])
        
    async def disconnect(self, channel_id: str, websocket: WebSocket):
        if self.active_connections.get(channel_id): 
            self.active_connections[channel_id].remove(websocket)
            count = self.connection_count(channel_id)
            ws_channel = connections[channel_id]
            for ws in ws_channel:
                await ws.send_text(f"Connection count: {count}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, channel_id: str, message: str, sender: str, not_send: WebSocket = None):
        connections = self.active_connections
        if connections.get(channel_id):
            ws_channel = connections[channel_id]
            for ws in ws_channel:
                ws: WebSocket = ws
                if ws != not_send:
                    await ws.send_text(f"Message: {message}. Sender: {sender}")
                
            
manager = ConnectionManager()

@router.get("/{channel_id}")
async def get(channel_id: str):
    return HTMLResponse(get_html(channel_id))
        
@router.websocket("/ws/{channel_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, channel_id: int):
    await manager.connect(websocket, channel_id)
    await manager.broadcast(channel_id, f"Client #{client_id} joined the chat", "SERVER")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(channel_id, f"Client #{client_id} says: {data}", client_id, websocket)
    except WebSocketDisconnect:
        manager.disconnect(channel_id, websocket)
        await manager.broadcast(channel_id, f"Client #{client_id} left the chat", "SERVER", websocket)