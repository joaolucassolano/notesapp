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

# TODO user EasyMDE in Frontend
def get_html(channel_id: str):
    return f"""
        <!DOCTYPE html>
        <html>
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Markdown Colaborative Note</title>
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            <style>
                textarea, #markdown-output {{
                    width: 45%;
                    height: 400px;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    font-size: 16px;
                    vertical-align: top;
                }}
                #markdown-output {{
                    overflow-y: auto; /* Add a scrollbar if content is long */
                }}
            </style>
        </head>
            <body>
                <h1>WebSocket Chat for Channel: {channel_id}</h1>
                <h2>Your ID: <span id="ws-id"></span></h2>
                <form action="" onsubmit="sendMessage(event)">
                    <textarea id="note"># Hello, Markdown!</textarea>
                    <div id="markdown-output"></div>
                </form>
                <ul id='messages'>
                </ul>
                <script>
                    const client_id = Date.now();
                    const channel_id = "{channel_id}"; // Get channel_id from Python
                    document.querySelector("#ws-id").textContent = client_id;
                    
                    // CHANGED: Correct WebSocket URL format
                    const ws = new WebSocket(`ws://localhost:8000/websocket/ws/${{channel_id}}/${{client_id}}`);
                    
                    const ul_messages = document.getElementById('messages');
                    
                    ws.onmessage = function(event) {{
                        const message = JSON.parse(event.data);
                        
                        switch (message.type) {{
                            case 'userJoined': {{
                                console.log(`(Internal action) User ${{message.data.username}} joined.`);
                                
                                const li_message = document.createElement('li');
                                const content = document.createTextNode(`User ${{message.data.username}} joined.`);
                                li_message.appendChild(content);
                                ul_messages.appendChild(li_message);
                        
                                break;
                            }}
                            
                            case 'noteUpdate': {{
                                console.log(message)
                                const noteTextarea = document.getElementById("note");
                                noteTextarea.value = message.data;
                                break;
                            }}
                                
                            case 'userLeft': {{
                                console.log(`(Internal action) User ${{message.data.username}} left.`);
                                
                                const li_message = document.createElement('li');
                                const content = document.createTextNode(`User ${{message.data.username}} left.`);
                                li_message.appendChild(content);
                                ul_messages.appendChild(li_message);
                        
                                break;
                            }}
                            
                            case 'count': {{
                                console.log(`(Internal action) User count ${{message.data}}.`);
                                break;
                            }}
                                
                                
                            default:
                                console.warn('Received unknown message type:', message);
                            
                        }}
                        

                    }};
                    
                    function sendMessage(event) {{
                        const input = document.getElementById("messageText");
                        // CHANGED: ws.send() only takes one argument
                        ws.send(input.value);
                        input.value = '';
                        event.preventDefault();
                    }}
                    
                    const noteTextarea = document.getElementById("note");
                    const markdownOutput = document.getElementById('markdown-output');
                    function renderMarkdown() {{
                        // Get the current text from the textarea
                        const markdownText = noteTextarea.value;
                        
                        // Convert the Markdown text to HTML using marked.parse()
                        const html = marked.parse(markdownText);
                        
                        // Set the innerHTML of the output div to the result
                        markdownOutput.innerHTML = html;
                    }}
                    renderMarkdown();
                    function handleTyping(event) {{
                        const currentText = event.target.value;
                        const joinNotification = {{ 
                            type: 'noteUpdate',
                            data: currentText
                        }};

                        ws.send(JSON.stringify(joinNotification));
                        renderMarkdown();
                    }}
                    noteTextarea.addEventListener("input", handleTyping);
                </script>
            </body>
        </html>
        """
        
from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    type: str
    data: dict

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
            await ws.send_json({'type': 'count', 'data': count})
        
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
                await ws.send_json({'type': 'count', 'data': count})
        
    async def send_personal_message(self, message: Message, websocket: WebSocket):
        await websocket.send_json(message)
        
    async def broadcast(self, channel_id: str, message: Message, sender: str, not_send: WebSocket = None):
        connections = self.active_connections
        if connections.get(channel_id):
            ws_channel = connections[channel_id]
            for ws in ws_channel:
                ws: WebSocket = ws
                if ws != not_send:
                    await ws.send_json(message)
                
            
manager = ConnectionManager()

@router.get("/{channel_id}")
async def get(channel_id: str):
    return HTMLResponse(get_html(channel_id))
        
@router.websocket("/ws/{channel_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, channel_id: int):
    await manager.connect(websocket, channel_id)
    await manager.broadcast(channel_id, {'type': 'userJoined', 'data': {'username': client_id}}, "SERVER")
    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_personal_message(data, websocket)
            await manager.broadcast(channel_id, data, client_id, websocket)
    except WebSocketDisconnect:
        manager.disconnect(channel_id, websocket)
        await manager.broadcast(channel_id, {'type': 'userLeft', 'data': {'username': client_id}}, "SERVER", websocket)