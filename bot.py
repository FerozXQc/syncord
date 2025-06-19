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


async def sendFile(filepath:str):
    channel_id = int(config('CHANNEL_ID'))
    channel = bot.get_channel(channel_id)

    if not channel:
        print('no channel found')
        return False

    file_data = r.get(filepath)
    if not file_data:
        print('no file data found')
        return False

    try:
        fileObj = BytesIO(file_data)
        fileObj.name = f'{filepath}.dat'
        msg = await channel.send(file=discord.File(fileObj))
        r.delete(filepath)    
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


def updateListItem(filename:str, new_data:str, json_path='files.json'):
    with open(json_path,'r+')  as file:
        data = json.load(file)
        while True:
            if filename in data['files']:
                filename+='(1)'
            else:
                break
        try:
            data['files'][filename] = [new_data]
            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()
            return 'ok done'
        except Exception as e:
            return f'error:{e}'


def fetchList(json_path='files.json'):
    listContent = []
    id=1
    with open(json_path,'r+') as file:
        data = json.load(file)
        for i in data['files']:
            listContent.append(i)
            id+=1
    return listContent

def fetchFile(filename:str, json_path='files.json'):
    with open(json_path, 'r+') as file:
        data = json.load(file)
        fetched_file = None
        if filename in data['files']:
            fetched_file = data['files'][filename][0]
            
        if not fetched_file:
            return False
        else:
            return fetched_file
        

# bot.run(token,log_handler=handler, log_level=logging.DEBUG)