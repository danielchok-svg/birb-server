import asyncio
import json
import os
from aiohttp import web
import websockets

connected_clients = set()

# -----------------------------
# WebSocket handler for birb clients
# -----------------------------
async def ws_handler(websocket, path):
    connected_clients.add(websocket)
    print("Birb client connected")

    try:
        async for _ in websocket:
            pass
    except:
        pass
    finally:
        connected_clients.remove(websocket)
        print("Birb client disconnected")

# -----------------------------
# Broadcast helper
# -----------------------------
async def broadcast(message: dict):
    if connected_clients:
        data = json.dumps(message)
        await asyncio.wait([client.send(data) for client in connected_clients])

# -----------------------------
# HTTP API endpoints
# -----------------------------
async def spawn(request):
    amount = int(request.match_info.get("amount", 1))
    await broadcast({"spawn_birb": amount})
    return web.Response(text=f"Spawned {amount} birbs")

async def despawn(request):
    await broadcast({"despawn_all": True})
    return web.Response(text="Despawned all birbs")

async def pause(request):
    await broadcast({"pause": True})
    return web.Response(text="Paused all birbs")

async def resume(request):
    await broadcast({"resume": True})
    return web.Response(text="Resumed all birbs")

async def chat(request):
    msg = request.match_info.get("msg", "")
    await broadcast({"chat": msg})
    return web.Response(text=f"Sent chat: {msg}")

# -----------------------------
# Create HTTP app
# -----------------------------
def create_http_app():
    app = web.Application()
    app.router.add_get("/spawn/{amount}", spawn)
    app.router.add_get("/despawn", despawn)
    app.router.add_get("/pause", pause)
    app.router.add_get("/resume", resume)
    app.router.add_get("/chat/{msg}", chat)
    return app

# -----------------------------
# Main entry point
# -----------------------------
async def main():
    port = int(os.environ.get("PORT", 10000))

    # Start WebSocket server
    ws_server = websockets.serve(ws_handler, "0.0.0.0", port + 1)

    # Start HTTP server
    http_app = create_http_app()
    http_runner = web.AppRunner(http_app)
    await http_runner.setup()
    http_site = web.TCPSite(http_runner, "0.0.0.0", port)

    print(f"HTTP API running on port {port}")
    print(f"WebSocket running on port {port+1}")

    await asyncio.gather(
        ws_server,
        http_site.start()
    )

if __name__ == "__main__":
    asyncio.run(main())