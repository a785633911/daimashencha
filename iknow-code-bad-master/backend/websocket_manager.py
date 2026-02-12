from fastapi import WebSocket
from typing import Dict, Set
import asyncio
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.task_connections: Dict[str, str] = {}  # task_id -> connection_id

    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        # Remove task associations
        tasks_to_remove = [task_id for task_id, conn_id in self.task_connections.items() if conn_id == connection_id]
        for task_id in tasks_to_remove:
            del self.task_connections[task_id]

    def bind_task(self, task_id: str, connection_id: str):
        self.task_connections[task_id] = connection_id

    async def send_message(self, connection_id: str, message: dict):
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except Exception as e:
                print(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def send_to_task(self, task_id: str, message: dict):
        if task_id in self.task_connections:
            connection_id = self.task_connections[task_id]
            await self.send_message(connection_id, message)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(connection_id)

        for connection_id in disconnected:
            self.disconnect(connection_id)

manager = ConnectionManager()
