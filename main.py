import discord
import discord.ext
from os import getenv
import asyncio
import aiohttp
import re
from discord.ext import commands, tasks
from keep_alive import keep_alive

intents=discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="s!", intents=intents)

now_status = 0

@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました^o^')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
        status.start()
        
    except Exception as e:
        print(f'Error syncing commands: {e}')

@tasks.loop(seconds=10)
async def status():
    global now_status

    if now_status == 0:
        data1 = discord.Activity(type=discord.ActivityType.playing, name="Scratchプロジェクトリンク展開")
        now_status = 1
    elif now_status == 1:
        data1 = discord.Activity(type=discord.ActivityType.competing, name=f"{len(bot.guilds)}サーバー")
        now_status =0

    await bot.change_presence(activity=data1)

async def scratch_expand(channel_id:int, id:int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.scratch.mit.edu/projects/{id}/") as resp:
            data = await resp.json()
            print(data)
            embeds = []
            embeds.append(discord.Embed(
                title=data["title"],
                url=f"https://scratch.mit.edu/projects/{id}/",
                color=0xfda747,
            ))
            if data["instructions"] != None:
                embeds.append(discord.Embed(
                    title="使い方",
                    description=data["instructions"],
                    color=0xfda747
                ))
            if data["description"] != None:
                embeds.append(discord.Embed(
                    title="メモとクレジット",
                    description=data["description"],
                    color=0xfda747
                ))
            embeds.append(discord.Embed(
                title="ステータス",
                description=f"<:loves:1335612168388739072> : {data['stats']['loves']} | <:fav:1335612107688775702> : {data['stats']['favorites']} | <:remix:1335612215918727238> : {data['stats']['remixes']} | <:views:1335612280515203244> : {data['stats']['views']}",
                color=0xfda747
            ))
            embeds[0].set_author(name=data["author"]["username"],icon_url=data["author"]["profile"]["images"]["90x90"])
            embeds[0].set_thumbnail(url=data["image"])

            await bot.get_channel(channel_id).send(embeds=embeds)

@bot.event
async def on_message(message:discord.Message):
    message_content = message.content
    channel_id = message.channel.id

    if "scratch.mit.edu/projects/" in message.content:
        one_re = re.findall('scratch.mit.edu/projects/.*', message.content)
        url_re_id = []
        for i in one_re:
            url_re_id.append(re.findall('[0-9]+', i)[0])
        print(url_re_id)
        
        for i in url_re_id:
            await scratch_expand(channel_id=channel_id,id=i)

try:
    keep_alive()
    bot.run(getenv("TOKEN"))
except Exception as e:
    print(f'エラーが発生しました: {e}')
