#!/usr/bin/env python3
import asyncio
import json

from pathlib import Path

import websockets


data_path = Path('../client/data.json')
data = json.loads(data_path.read_text())
uri = data['ServiceEndpointWebsocket']


async def echo():
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            print(message)        

asyncio.get_event_loop().run_until_complete(echo())
