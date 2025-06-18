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

async def fetchFile(message_id:str):
    channel_id = int(config('CHANNEL_ID'))
    channel = bot.get_channel(channel_id)
    if channel:
        try:
            msg = await channel.get_message(message_id)
            if msg.attachments[0]:
                filename = msg.attachments.filename
                url = msg.attachments.url
                async with aiohttp.session() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            return data
        except Exception as e:
            await channel.send(f'file couldnt be fetched, error:{e}')
            return False
    else:
        return f'no channel with the id {channel_id}.'

def file_exists(check_file, filename='files.json'):
    try:
        with open(filename, 'r') as file:
            file_data = json.load(file)

            # Make sure 'files' exists and is a list with at least one dict
            if 'files' in file_data and isinstance(file_data['files'], list) and len(file_data['files']) > 0:
                first_entry = file_data['files'][0]

                if check_file in first_entry:
                    print(first_entry[check_file])
                    return first_entry[check_file]
    except Exception as e:
        print(f"Error reading file: {e}")

    return False

def updateList(new_data, filename='files.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data['files'].append(new_data)
        file.seek(0)
        json.dump(file_data,file,indent=1)


# def deleteList(del_data:str, filename='files.json'):
#     with open(filename,'r+') as file:
#         file_data = json.load(file)
#         if del_data in file_data['files'][0]:
#             print('it exists in list')
#             del file_data['files'][0][del_data]
#             file.seek(0)
#             json.dump(file_data, file, indent=4)
#             file.truncate() 
#         else:
#             print('cant find the file to delete')



# x={
#     'file1':[
#         {
#             'item':'ok'
#         }
#     ]
# }

# deleteList('file1')


# bot.run(token,log_handler=handler, log_level=logging.DEBUG)