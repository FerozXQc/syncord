from fastapi import FastAPI, File, UploadFile
import uvicorn
from bot import (
    bot,
    sendFile,
    fetchChunk,
    fetchIndex,
    sendIndexFile,
    appendIndex,
    deleteIndex,
    updateIndex,
    fetchList,
    fetchFileData,
)
from decouple import config
import asyncio
import time
from io import BytesIO
from redis_client import r
import aiofiles
import json
import os

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    async def start_bot_and_fetch():
        await bot.wait_until_ready()
        await fetchIndex()

    asyncio.create_task(bot.start(config("DISCORD_TOKEN")))
    asyncio.create_task(start_bot_and_fetch())


# use this to initialise the index.json file and get its message Id
@app.post("/createIndexFile")
async def init_index():
    result = await sendIndexFile()
    await fetchIndex()


# USE THIS ONCE AND NOTE DOWN YOUR MESSAGE ID.


@app.get("/")
def hello():
    return "hewwo:3"


@app.post("/sendFile")
async def send_file_to_discord(file: UploadFile = File(...)):
    chunk_size = 8 * 1024 * 1024  # 8mb
    chunk_num = 1
    # time_taken=0
    file_path = file.filename
    chunk_list = []
    while True:
        # start = time.perf_counter()
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        key = f"{file_path}_{str(chunk_num).zfill(6)}"
        file_id = await sendFile(key, chunk)
        chunk_list.append({"message_id": file_id, "chunk_num": chunk_num})
        chunk_num += 1

    result = appendIndex(new_data=chunk_list, file_path=file_path)
    await updateIndex()
    return result


@app.post("/viewListItem")
def viewListItem():
    listContent = fetchList()
    if listContent == []:
        return "list is empty"
    else:
        return listContent


@app.delete("/deleteListItem")
async def deleteListItem(filename: str, json_path="files.json"):
    channel_id = int(config("CHANNEL_ID"))
    channel = bot.get_channel(channel_id)

    if not channel:
        return "channel not found"

    fetched_data = fetchFileData(filename)
    print(fetched_data)
    if not fetched_data:
        return "file not found"
    for chunk in fetched_data:
        print(chunk["message_id"])
        try:
            msg = await channel.fetch_message(int(chunk["message_id"]))
            await msg.delete()
        except Exception as e:
            print(f"failed to get message: {e}")
            return False

    result = deleteIndex(filename)
    await updateIndex()
    return result


@app.post("/recieveFile")
async def recieveFile(filename: str):
    channel_id = int(config("CHANNEL_ID"))
    channel = bot.get_channel(channel_id)

    if not channel:
        return "channel not found"
    fetched_data = fetchFileData(filename)
    if not fetched_data:
        return "file not found"
    while True:
        if os.path.exists(filename):
            filename += "(1)"
        else:
            break
    async with aiofiles.open(filename, "wb") as file:
        for chunk in fetched_data:

            data = await fetchChunk(chunk["message_id"], channel)
            if not data:
                return f"Failed to fetch chunk {chunk['message_id']}"
            await file.write(data)
    return f"file:{filename} saved"


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
