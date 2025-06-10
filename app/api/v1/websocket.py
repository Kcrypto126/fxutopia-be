from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import json

from ...database import get_db
from ...utils.websocket_manager import manager
from ...services.auth_service import AuthService

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    user_id = None
    
    # Authenticate user if token provided
    if token:
        try:
            auth_service = AuthService(db)
            # You'll need to implement token verification in auth_service
            user = auth_service.verify_websocket_token(token)
            if user:
                user_id = user.id
        except:
            pass
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "join_room":
                room_id = message_data.get("room_id")
                await manager.join_room(websocket, room_id)
                await manager.send_personal_message(
                    json.dumps({"type": "joined_room", "room_id": room_id}),
                    websocket
                )
            
            elif message_type == "leave_room":
                room_id = message_data.get("room_id")
                await manager.leave_room(websocket, room_id)
                await manager.send_personal_message(
                    json.dumps({"type": "left_room", "room_id": room_id}),
                    websocket
                )
            
            elif message_type == "room_message":
                room_id = message_data.get("room_id")
                message = message_data.get("message")
                await manager.broadcast_to_room(
                    {
                        "type": "room_message",
                        "room_id": room_id,
                        "message": message,
                        "user_id": user_id
                    },
                    room_id
                )
            
            elif message_type == "typing":
                room_id = message_data.get("room_id")
                await manager.broadcast_to_room(
                    {
                        "type": "typing",
                        "room_id": room_id,
                        "user_id": user_id,
                        "is_typing": message_data.get("is_typing", False)
                    },
                    room_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)