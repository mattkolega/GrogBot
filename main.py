import asyncio
from os import environ

import discord
from discord.ext import commands
from dotenv import load_dotenv

discord.utils.setup_logging()  # Enables bot logging in console

load_dotenv()
TOKEN = environ["BOT_TOKEN"]

description = """
   ______                 ____        __ 
  / ____/________  ____ _/ __ )____  / /_
 / / __/ ___/ __ \/ __ `/ __  / __ \/ __/
/ /_/ / /  / /_/ / /_/ / /_/ / /_/ / /_  
\____/_/   \____/\__, /_____/\____/\__/  
                /____/                   

Built using discord.py
"""
intents = discord.Intents.all()
helpCommand = commands.DefaultHelpCommand(no_category="Misc")

bot = commands.Bot(command_prefix="$", description=description, intents=intents, help_command=helpCommand)
bot.activity = discord.Activity(type=discord.ActivityType.listening, name="Get on the Beers")

initialExtensions = [
    "cogs.anime",
    "cogs.fun",
    "cogs.minecraft",
    "cogs.music",
    "cogs.quote",
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

async def main():
    async with bot:
        await loadExtensions()
        await bot.start(TOKEN)

asyncio.run(main())