import asyncio
import websockets

async def test_websocket():
    uri = "wss://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net/ws"
    try:
        # Connect to the WebSocket server
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            while True:
                # Receive messages from the server
                response = await websocket.recv()
                print(f"Received: {response}")
    except Exception as e:
        print(f"Error connecting to WebSocket: {e}")

asyncio.get_event_loop().run_until_complete(test_websocket())
