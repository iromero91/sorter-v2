from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from defs.events import IdentityEvent, MachineIdentityData
from blob_manager import getMachineId
from bricklink.api import getPartInfo

app = FastAPI(title="Sorter API", version="0.0.1")

active_connections: List[WebSocket] = []
server_loop: Optional[asyncio.AbstractEventLoop] = None


@app.on_event("startup")
async def onStartup() -> None:
    global server_loop
    server_loop = asyncio.get_running_loop()


MACHINE_ID = getMachineId()


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    active_connections.append(websocket)

    identity_event = IdentityEvent(
        tag="identity", data=MachineIdentityData(machine_id=MACHINE_ID, nickname=None)
    )
    await websocket.send_json(identity_event.model_dump())

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def broadcastEvent(event: dict) -> None:
    dead_connections = []
    for connection in active_connections[:]:
        try:
            await connection.send_json(event)
        except Exception:
            dead_connections.append(connection)
    for conn in dead_connections:
        if conn in active_connections:
            active_connections.remove(conn)


class BricklinkPartResponse(BaseModel):
    no: str
    name: str
    type: str
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    weight: Optional[str] = None
    dim_x: Optional[str] = None
    dim_y: Optional[str] = None
    dim_z: Optional[str] = None
    year_released: Optional[int] = None
    is_obsolete: Optional[bool] = None


@app.get("/bricklink/part/{part_id}", response_model=BricklinkPartResponse)
def getBricklinkPart(part_id: str) -> BricklinkPartResponse:
    data = getPartInfo(part_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Part not found")
    return BricklinkPartResponse(**data)
