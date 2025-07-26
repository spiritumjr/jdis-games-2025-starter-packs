import asyncio
import aiohttp
import traceback
import os
from .types import ServerMessage, ServerMessageTickInfo, ServerMessageTickInfoDead, ServerMessageInfo, LinkMessage, SetActionMessage, ServerMessageGameStart, ServerMessageIncorrectLogin
from .bot import TOKEN, on_tick, on_game_start

# A tick on the backend is 500ms. Give at most 450ms of compute time to account
# for network latency and variance.
MAX_TICK_COMPUTE_TIME = 0.450

isFirstTick = True

async def on_message(data):
    global isFirstTick
    msg = ServerMessage.from_json(data)
    match msg:
        case ServerMessageGameStart():
            isFirstTick = False
            await on_game_start()
        case ServerMessageTickInfo():
            try:
                async with asyncio.timeout(MAX_TICK_COMPUTE_TIME):
                    if isFirstTick:
                        isFirstTick = False
                        await on_game_start()
                    action = await on_tick(msg.state)
                return SetActionMessage(action).to_json()
            except TimeoutError:
                print("WARNING: Your on_tick function was cancelled because it was taking too long.")
        case ServerMessageTickInfoDead():
            print("You are dead...")
        case ServerMessageInfo():
            return ConfirmMessage(TOKEN)
        case ServerMessageIncorrectLogin():
            print(f"Token '{TOKEN}' is not valid.")
            exit()

async def main():
    WS = os.getenv("WS", "ws")
    async with aiohttp.ClientSession() as client:
        async with client.ws_connect(f"wss://games.jdis.ca/{WS}") as ws:
            await ws.send_str(LinkMessage(TOKEN).to_json())
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        reply = await on_message(msg.data)
                        if reply:
                            await ws.send_str(reply)
                    except Exception as e:
                        traceback.print_exception(e)

if __name__ == "__main__":
    asyncio.run(main())
