import discord
from discord.ext import commands
import logging
from decouple import config
import os
from io import BytesIO
import json
import aiohttp
from redis_client import r
token = config('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
    print(f'its ON!, {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        ...
    if 'shit' in message.content.lower():
        await message.delete()
        await message.channel.send(f'dont say that {message.author.mention}')
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f'hello! {ctx.author.mention}')


async def sendIndexFile(filename='Index.json'):
    channel_id = int(config('CHANNEL_ID'))
    channel = bot.get_channel(channel_id)
    
    if not channel:
        print('No channel found')
        return False

    # Prepare index data
    data = {
        "files": {}
    }

    json_string = json.dumps(data, indent=2)
    file_bytes = BytesIO(json_string.encode('utf-8'))
    file_bytes.name = filename

    env_path = '.env'
    index_key = 'INDEX_ID'

    # Check .env file
    if not os.path.exists(env_path):
        return 'No .env file found!!'

    with open(env_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.strip().replace(" ", "").startswith(f"{index_key}="):
                print('INDEX_ID already exists!')
                raise HTTPException(status_code=400, detail="INDEX_ID already exists!")

    # Send file to Discord
    msg = await channel.send(files=[discord.File(file_bytes)])
    # Append INDEX_ID to .env
    with open(env_path, 'a') as f:
        f.write(f'\n{index_key}={msg.id}\n')
    print(f"Index file sent. Message ID: {msg.id}")
    return True


async def sendFile(filepath:str,chunk):
    channel_id = int(config('CHANNEL_ID'))
    channel = bot.get_channel(channel_id)

    if not channel:
        print('no channel found')
        return False

    file_data = chunk
    if not file_data:
        print('no file data found')
        return False
    try:
        fileObj = BytesIO(file_data)
        fileObj.name = f'{filepath}.dat'
        msg = await channel.send(file=discord.File(fileObj))
        return msg.id
    except Exception as e:
        print(f'error:{e}')
        return False    

async def fetchChunk(message_id:int,channel:int):
    try:
        msg = await channel.fetch_message(message_id)
        if msg.attachments[0]:
            attachment = msg.attachments[0]
            filename = attachment.filename
            url = attachment.url

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return data
    except Exception as e:
        return False
        
async def fetchIndex():
    message_id = int(config('INDEX_ID'))
    channel = bot.get_channel(int(config('CHANNEL_ID')))
    if not channel:
        return 'no channel'
    msg = await channel.fetch_message(message_id)
    if not msg.attachments:
        return 'no file found.'
    attachment = msg.attachments[0]
    filename = "Index.json"
    url = attachment.url
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                content = await resp.read()
                r.set(filename,content)
            else:
                return f'failed to fetch {filename}'

def appendIndex(new_data,file_path,indexFile="Index.json"):
    indexJSON = r.get(indexFile)
    if not indexJSON:
        return 'index file not found'
        
    data = json.loads(indexJSON)
    while file_path in data['files']:
        file_path+='(1)'
    data['files'][file_path] = new_data
    r.set(indexFile,json.dumps(data))
    return 'file appended successfully'

def deleteIndex(del_filename, indexFile="Index.json"):
    indexJSON = r.get(indexFile)
    if not indexJSON:
        return 'index file not found'
    data = json.loads(indexJSON)
    if del_filename in data['files']:
        del data['files'][del_filename]
        r.set(indexFile,json.dumps(data))
    
        return f"{del_filename} removed from index."
    else:
        return f"{del_filename} not found in index."
    
def fetchList(indexFile='Index.json'):
    listContent = []
    indexJSON = r.get(indexFile)
    if not indexJSON:
        return 'index file not found'
    id = 1
    data = json.loads(indexJSON)
    for i in data['files']:
        listContent.append(i)
        id+=1
    return listContent

def fetchFileData(filename:str, indexFile='Index.json'):
    indexJSON = r.get(indexFile)
    if not indexJSON:
        return False
    data = json.loads(indexJSON)
    fetched_file = data['files'][filename] 
    # print(fetched_file) debugging
    if not fetched_file:
        return False
    else:
        return fetched_file

async def updateIndex(indexFile="Index.json"):
    message_id = int(config('INDEX_ID'))
    channel = bot.get_channel(int(config('CHANNEL_ID')))
    indexJSON = r.get(indexFile)
    if not indexJSON:
        return 'index file not found'
    data = json.loads(indexJSON)
    json_string = json.dumps(data, indent=2)
    file_bytes = BytesIO(json_string.encode('utf-8'))
    file_bytes.name = "Index.json"
    if not channel:
        return 'no channel'
    msg = await channel.fetch_message(message_id)
    await msg.edit(attachments=[discord.File(file_bytes)])

# bot.run(token,log_handler=handler, log_level=logging.DEBUG)
