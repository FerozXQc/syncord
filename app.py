from fastapi import FastAPI, File, UploadFile
import uvicorn
from bot import bot, sendFile, updateListItem, fetchList, fetchFile, fetchChunk
from decouple import config
import asyncio
from redis_client import r
import time
import aiofiles
import json
import os

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
    # time_taken=0
    file_path = file.filename
    chunk_list = []
    while True:
        # start = time.perf_counter()
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        key = f'{file_path}_{str(chunk_num).zfill(6)}'
        r.set(key,chunk)
        file_id = await sendFile(key)
        chunk_list.append({'message_id':file_id, 'chunk_num':chunk_num})
        # end = time.perf_counter()
        # time_taken+= round(end-start,2)
        # print(file_id,time_taken)
        chunk_num+=1
    # print(time_taken/chunk_num)##to check the upload speed..   
    result = updateListItem(file_path, chunk_list)
    print(result)



@app.post('/viewListItem')
def viewListItem():
    listContent = fetchList()
    if listContent == []:
        return 'list is empty'
    else:
        return listContent
 
@app.delete('/deleteListItem')
async def deleteListItem(filename:str,json_path='files.json'):
    channel_id = int(config('CHANNEL_ID'))
    channel = bot.get_channel(channel_id)

    if not channel:
        return 'channel not found'

    fetched_data = fetchFile(filename)
    if not fetched_data:
        return 'file not found'
    for chunk in fetched_data:
        try:
            msg = await channel.fetch_message(int(chunk['message_id']))
            await msg.delete()
        except Exception as e:
            print(f"Failed to delete message {chunk['message_id']}: {e}")
    
    with open(json_path,'r+') as file:
        data = json.load(file)
        del data['files'][filename]
        file.seek(0)
        json.dump(data, f, indent=2)
        file.truncate()
        return 'deleted'
   
@app.post('/recieveFile')
async def recieveFile(filename:str):
    channel_id = int(config('CHANNEL_ID'))
    channel = bot.get_channel(channel_id)
   
    if not channel:
        return 'channel not found'
    fetched_data = fetchFile(filename)
    if not fetched_data:
        return 'file not found'
    while True:
        if os.path.exists(filename):
            filename+='(1)'
        else:
            break
    async with aiofiles.open(filename,'wb') as file:
        for chunk in fetched_data:

            data =await fetchChunk(chunk['message_id'],channel)
            if not data:
                return f"Failed to fetch chunk {chunk['message_id']}"
            await file.write(data)
    return f'file:{filename} saved'

if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)