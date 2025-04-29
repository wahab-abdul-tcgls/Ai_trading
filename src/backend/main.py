# backend/main.py

import asyncio
import json
import ssl
import websockets
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from generated import MarketDataFeedV3_pb2 as pb
from dotenv import load_dotenv
import os
import sys
import os
import requests
from google.protobuf.json_format import MessageToDict
from generated import MarketDataFeedV3_pb2 as pb

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hold connected clients
connected_clients = set()

def get_market_data_feed_authorize_v3():
    """Get authorization for market data feed."""
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    url = 'https://api.upstox.com/v3/feed/market-data-feed/authorize'
    api_response = requests.get(url=url, headers=headers)
    return api_response.json()

def decode_protobuf(buffer):
    """Decode protobuf message."""
    feed_response = pb.FeedResponse()
    feed_response.ParseFromString(buffer)
    return feed_response

async def upstox_websocket_handler():
    """Connect to Upstox WebSocket and forward data to frontend clients."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    response = get_market_data_feed_authorize_v3()
    if "data" not in response:
        print("Error fetching Upstox authorized_redirect_uri:", response)
        return

    uri = response["data"]["authorized_redirect_uri"]

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        print("✅ Connected to Upstox WebSocket feed!")

        # Subscribe to instruments
        data = {
            "guid": "someguid",
            "method": "sub",
            "data": {
                "mode": "full",
                "instrumentKeys": ["NSE_INDEX|Nifty Bank", "NSE_INDEX|Nifty 50"]
            }
        }
        binary_data = json.dumps(data).encode('utf-8')
        await websocket.send(binary_data)

        while True:
            message = await websocket.recv()
            decoded_data = decode_protobuf(message)
            data_dict = MessageToDict(decoded_data)

            # Broadcast to all connected frontend clients
            if connected_clients:
                message_text = json.dumps(data_dict)
                await asyncio.gather(*[client.send_text(message_text) for client in connected_clients])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Just keep the connection alive
    except Exception as e:
        print("WebSocket disconnected:", e)
    finally:
        connected_clients.remove(websocket)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(upstox_websocket_handler())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
