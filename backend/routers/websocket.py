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
import controllers.notes as notes_controller
from db.database import get_db_conn
from models.note import Note
import asyncpg


router =  APIRouter()

# TODO user EasyMDE in Frontend
def get_html(note: Note):
    return f"""
        <!DOCTYPE html>
        <html>
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{note.title}</title>
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
                <h1>WebSocket Chat for Channel: {note.title}</h1>
                <h2>Your ID: <span id="ws-id"></span></h2>
                <form action="" onsubmit="sendMessage(event)">
                    <textarea id="note"></textarea>
                    <div id="markdown-output"></div>
                </form>
                <ul id='messages'>
                </ul>
                <script>
                    const user_id = Date.now();
                    const note_id = "{note.id}"; // Get note_id from Python
                    document.querySelector("#ws-id").textContent = user_id;
                    
                    // CHANGED: Correct WebSocket URL format
                    const ws = new WebSocket(`ws://localhost:8000/websocket/ws/${{note_id}}/${{user_id}}`);
                    
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
                            
                            case 'noteSync': {{
                                console.log('Received full note state sync');
                                const noteTextarea = document.getElementById("note");
                                noteTextarea.value = message.data.content;
                                renderMarkdown();
                                break;
                            }}
                            
                            case 'noteUpdate': {{
                                console.log('Received note update from another user.');
                                const noteTextarea = document.getElementById("note");
                                noteTextarea.value = message.data.content;
                                renderMarkdown();
                                
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
                        console.log({dict(note)});
                        const currentText = event.target.value;
                        const joinNotification = {{ 
                            type: 'noteUpdate',
                            data: {{id: {note.id}, content: currentText, title: '{note.title}'}}
                        }};
                        console.log(joinNotification)
                        ws.send(JSON.stringify(joinNotification));
                        renderMarkdown();
                    }}
                    noteTextarea.addEventListener("input", handleTyping);
                    
                    document.addEventListener('keydown', function(event) {{
                        if (event.key === 's' && (event.ctrlKey || event.metaKey)) {{
                            // Previne a ação padrão do navegador.
                            event.preventDefault();

                            // Mensagem de log para confirmar a detecção.
                            console.log('Combinação "Ctrl+S" detectada.');
                            enviarDadosParaBackend();
                        }}
                    }});
                    
                    function enviarDadosParaBackend() {{
                        const note = {{
                            'title': '{note.title}',
                            'content': noteTextarea.value,
                            'id': {note.id}
                        }};
                        fetch('http://127.0.0.1:8000/notes/{note.id}', {{
                            method: 'PUT',
                            headers: {{
                            'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify(note),
                        }})
                        .then(response => {{
                            if (!response.ok) {{
                            throw new Error('Erro na requisição: ' + response.statusText);
                            }}
                            return response.json();
                        }})
                        .then(data => {{
                            console.log('Dados salvos com sucesso:', data);
                            // Adicione aqui qualquer feedback para o usuário, como uma notificação de sucesso.
                        }})
                        .catch((error) => {{
                            console.error('Falha ao salvar os dados:', error);
                            // Adicione aqui o tratamento de erro, como exibir uma mensagem para o usuário.
                        }});
                    }}
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
        self.active_connections: Dict[int, list[WebSocket]] = {}
        self.notes_state: Dict[int, dict] = {}
        
    async def broadcast_user_count(self, note_id: int):
        if self.active_connections.get(note_id):
            count = len(self.active_connections[note_id])
            message = {'type': 'count', 'data': count}
            for connection in self.active_connections[note_id]:
                await connection.send_json(message)
                
    async def update_and_broadcast(self, note_id: int, message: Message, sender: WebSocket):
        if message['type'] == 'noteUpdate':
            print(message)
            self.notes_state[note_id] = message['data']
            
        if self.active_connections.get(note_id):
            for connection in self.active_connections.get(note_id):
                if connection != sender:
                    await connection.send_json(message)
        
    async def connect(self, websocket: WebSocket, note_id: int, db_conn: asyncpg.Connection):
        await websocket.accept()
        
        if note_id not in self.notes_state:
            note_data = await notes_controller.get_note(db_conn, note_id)
            if note_data:
                self.notes_state[note_id] = dict(note_data)
            else:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        
        connections = self.active_connections
        if note_id not in connections:
            connections[note_id] = []
        connections[note_id].append(websocket)
        
        current_state = self.notes_state.get(note_id, {})
        await websocket.send_json({'type': 'noteSync', 'data': current_state})        
        await self.broadcast_user_count(note_id)
        
    async def disconnect(self, note_id: int, websocket: WebSocket, db_conn):
        if self.active_connections.get(note_id): 
            self.active_connections[note_id].remove(websocket)
            if not self.active_connections[note_id]:
                del self.active_connections[note_id]
                if note_id in self.notes_state:
                    await notes_controller.edit_note(db_conn, note_id, Note(**self.notes_state[note_id]))
                    del self.notes_state[note_id]
            else:
                await self.broadcast_user_count(note_id)
                
            
manager = ConnectionManager()

@router.get("/{note_id}")
async def get(note_id: int, db_conn: asyncpg.Connection = Depends(get_db_conn)):
    note_data = await notes_controller.get_note(db_conn, note_id)
    return HTMLResponse(get_html(Note(**note_data)))
    return Exception("No note found.")
        
@router.websocket("/ws/{note_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int, 
    note_id: int, 
    db_conn: asyncpg.Connection = Depends(get_db_conn)
):
    await manager.connect(websocket, note_id, db_conn)
    await manager.update_and_broadcast(note_id, {'type': 'userJoined', 'data': {'username': user_id}}, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.update_and_broadcast(note_id, data, websocket)
    except WebSocketDisconnect:
        await manager.disconnect(note_id, websocket, db_conn)
        await manager.update_and_broadcast(note_id, {'type': 'userLeft', 'data': {'username': user_id}}, websocket)