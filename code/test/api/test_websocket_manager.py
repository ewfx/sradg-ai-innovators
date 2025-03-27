
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from anomaly_detection.api.websocket_manager import ConnectionManager

@pytest.mark.asyncio
async def test_connection_manager_lifecycle():
    manager = ConnectionManager()
    mock_websocket = AsyncMock()
    
    await manager.connect(mock_websocket)
    assert mock_websocket in manager.active_connections

    manager.disconnect(mock_websocket)
    assert mock_websocket not in manager.active_connections

@pytest.mark.asyncio
async def test_send_personal_message():
    manager = ConnectionManager()
    mock_websocket = AsyncMock()
    await manager.connect(mock_websocket)

    await manager.send_personal_message("Hello!", mock_websocket)
    mock_websocket.send_text.assert_called_with("Hello!")

@pytest.mark.asyncio
async def test_broadcast_message():
    manager = ConnectionManager()
    websocket1 = AsyncMock()
    websocket2 = AsyncMock()

    await manager.connect(websocket1)
    await manager.connect(websocket2)

    await manager.broadcast("Broadcast message")
    websocket1.send_text.assert_called_with("Broadcast message")
    websocket2.send_text.assert_called_with("Broadcast message")
