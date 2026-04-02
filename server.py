import asyncio
import websockets
import json
import os

PORT = int(os.environ.get("PORT", 10000))
connected_clients = set()

async def handler(websocket):
    connected_clients.add(websocket)
    print("Client connected")

    try:
        async for _ in websocket:
            pass
    except:
        pass
    finally:
        connected_clients.remove(websocket)
        print("Client disconnected")

async def broadcast(message):
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

async def command_console():
    while True:
        cmd = input("Command: ").strip()

        if cmd.startswith("spawn"):
            parts = cmd.split()
            amount = 1
            if len(parts) > 1:
                try:
                    amount = int(parts[1])
                except:
                    pass
            msg = json.dumps({"spawn_birb": amount})
            await broadcast(msg)

        elif cmd == "despawn":
            msg = json.dumps({"despawn_all": True})
            await broadcast(msg)

        elif cmd.startswith("chat"):
            text = cmd[5:]
            msg = json.dumps({"chat": text})
            await broadcast(msg)

        elif cmd == "pause":
            msg = json.dumps({"pause": True})
            await broadcast(msg)

        elif cmd == "resume":
            msg = json.dumps({"resume": True})
            await broadcast(msg)

async def main():
    print(f"Server running on port {PORT}")
    server = await websockets.serve(handler, "0.0.0.0", PORT)
    await command_console()

asyncio.run(main())