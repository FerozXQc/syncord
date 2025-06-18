from fastapi import FastAPI, File, UploadFile
import uvicorn
from bot import bot, sendFile, updateList, file_exists
from decouple import config
import asyncio
from redis_client import r
import time
import json

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bot.start(config("DISCORD_TOKEN")))

@app.get('/')
def hello():
    return 'hewwo:3'

chunk_size = 8*1024*1024 #8mb

@app.post("/sendFile")
async def send_file_to_discord(file: UploadFile = File(...)):
    chunk_num=1
    time_taken=0
    pushJSON = {
        f"{file.filename}":[]
    }
    while True:
        # start = time.perf_counter()
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        key = f'{file.filename}_{str(chunk_num).zfill(6)}'
        r.set(key,chunk)
        file_id = await sendFile(key)
        pushJSON.setdefault(file.filename, []).append({key: file_id})

        # end = time.perf_counter()
        # time_taken+= round(end-start,2)
        # print(file_id,time_taken)
        chunk_num+=1
    # print(time_taken/chunk_num)##to check the upload speed..
    updateList(pushJSON)
    print(pushJSON)

@app.post('/getFile')
async def get_file_from_discord(filepath:str):
    result = file_exists(filepath)
    print(result)

    

if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)