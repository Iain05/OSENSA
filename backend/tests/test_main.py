import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from main import handle_order, on_message, on_connect, EVENT_LOOP


@pytest.mark.asyncio
async def test_handle_order_valid():
    """Test valid order: should publish to FOOD after sleeping."""
    mock_client = MagicMock()
    
    with patch("random.uniform", return_value=0.1), \
         patch("asyncio.sleep", new=AsyncMock()) as mock_sleep:

        await handle_order(mock_client, '{"food": "pizza", "table": 5}')
    
    mock_sleep.assert_awaited_with(0.1)
    mock_client.publish.assert_called_with("FOOD", '{"food": "pizza", "table": 5}')


@pytest.mark.asyncio
async def test_handle_order_invalid():
    """Test invalid order: no publish should occur."""
    mock_client = MagicMock()

    await handle_order(mock_client, '{"food": "", "table": 3}')
    mock_client.publish.assert_not_called()

    await handle_order(mock_client, 'not a json')
    mock_client.publish.assert_not_called()

    await handle_order(mock_client, '{"food": "burger"}')
    mock_client.publish.assert_not_called()

    await handle_order(mock_client, '{"food": "burger", "table": "not an int"}')
    mock_client.publish.assert_not_called()

    await handle_order(mock_client, '{"food": "  ", "table": 4}')
    mock_client.publish.assert_not_called()


def test_on_connect_calls_subscribe():
    client = MagicMock()
    on_connect(client, None, None, 0)
    client.subscribe.assert_called_once_with("ORDER")
