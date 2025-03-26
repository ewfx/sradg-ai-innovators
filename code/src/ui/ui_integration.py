# ui/ui_integration.py (UI Integration - Example using a simple HTML/JavaScript)

import asyncio
import websockets
import json

async def connect_websocket():
    uri = "ws://localhost:8000/ws"  # Replace with your FastAPI WebSocket URI
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket.")

        async def send_data():
            while True:
                trade_id = input("Enter TRADEID: ")
                risk_date = input("Enter RISKDATE: ")
                desk_name = input("Enter DESKNAME: ")
                quantity_difference = float(input("Enter QUANTITYDIFFERENCE: "))
                impact_price = float(input("Enter IMPACT_PRICE: "))
                impact_quantity = float(input("Enter IMPACT_QUANTITY: "))
                comment = input("Enter COMMENT: ")

                data = {
                    "TRADEID": int(trade_id),
                    "RISKDATE": risk_date,
                    "DESKNAME": desk_name,
                    "QUANTITYDIFFERENCE": quantity_difference,
                    "IMPACT_PRICE": impact_price,
                    "IMPACT_QUANTITY": impact_quantity,
                    "COMMENT": comment,
                }
                await websocket.send(json.dumps(data))
                await asyncio.sleep(1)

        async def receive_data():
            while True:
                message = await websocket.recv()
                print(f"Received message: {message}")

        await asyncio.gather(send_data(), receive_data())

if __name__ == "__main__":
    asyncio.run(connect_websocket())