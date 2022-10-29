import discord
from discord.ext import commands

from dotenv import load_dotenv
from os import environ

import asyncio

discord.utils.setup_logging()

load_dotenv()
TOKEN = environ["BOT_TOKEN"]
PLAYLIST = environ["PLAYLIST_URL"]

description = "GrogBot. Built using discord.py"
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="$", description=description, intents=intents)
bot.activity = discord.Activity(type=discord.ActivityType.listening, name="Get on the Beers")

initialExtensions = [
    "cogs.fun",
    "cogs.quote",
    "cogs.music"
]

async def loadExtensions():
    for extension in initialExtensions:
        await bot.load_extension(extension)

@bot.event
async def on_ready():
    """Executes when the bot has finished starting up"""
    print(f"We have logged in as {bot.user}")

@bot.command()
async def hello(ctx):
    """Responds to the user"""
    await ctx.send("G'day!")

@bot.command()
async def grogsongs(ctx):
    """Sends playlist link containing party songs"""
    await ctx.send(PLAYLIST)

async def main():
    async with bot:
        await loadExtensions()
        await bot.start(TOKEN)

asyncio.run(main())