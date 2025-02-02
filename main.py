import discord
import discord.ext
from os import getenv
import asyncio
import aiohttp
import re
from discord.ext import commands


intents=discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="s!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました^o^')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')

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
                description=f"<:love:1330407885934694411> : {data['stats']['loves']} | <:fav:1330407870990127145> : {data['stats']['favorites']} | <:remix:1330407897007521793> : {data['stats']['remixes']} | <:views:1330407909326065756> : {data['stats']['views']}",
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
