import asyncio
from os import environ

import discord
import motor.motor_asyncio
from discord.ext import commands
from dotenv import load_dotenv

discord.utils.setup_logging()  # Enables bot logging in console

load_dotenv()
TOKEN = environ["BOT_TOKEN"]
CONNECTION_STRING = environ["MONGODB_CONNECTION_STRING"]

description = """
   ______                
  / ____/________  ____ _
 / / __/ ___/ __ \/ __ `/
/ /_/ / /  / /_/ / /_/ / 
\____/_/   \____/\__, /  
    ____        /____/   
   / __ )____  / /_      
  / __  / __ \/ __/      
 / /_/ / /_/ / /_        
/_____/\____/\__/        
                         
Built using discord.py
"""
intents = discord.Intents.all()
helpCommand = commands.DefaultHelpCommand(no_category="Misc")

class GrogBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="$", description=description, intents=intents, help_command=helpCommand)
        self.activity = discord.Activity(type=discord.ActivityType.listening, name="Get on the Beers")

        self.databaseClient = motor.motor_asyncio.AsyncIOMotorClient(CONNECTION_STRING, serverSelectionTimeoutMS=30000)

bot = GrogBot()

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