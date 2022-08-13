import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import environ
import random

load_dotenv()
TOKEN = environ["BOT_TOKEN"]
PLAYLIST = environ["PLAYLIST_URL"]

description = "GrogBot. Built using discord.py"
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="$", description=description, intents=intents)
bot.activity = discord.Activity(type=discord.ActivityType.listening, name="Get on the Beers")

@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))

@bot.command()
async def hello(ctx):
    await ctx.send("G'day!")

@bot.command()
async def randomquote(ctx):
    channel = discord.utils.get(bot.get_all_channels(), name="quotes")
    messages = [message async for message in channel.history(limit=500)]
    randomIndex = random.randrange(0, len(messages))

    embed = discord.Embed(title="Random Quote")
    embed.description = messages[randomIndex].content
    embed.url = messages[randomIndex].jump_url

    await ctx.send(embed=embed)

@bot.command()
async def grogsongs(ctx):
    await ctx.send(PLAYLIST)

bot.run(TOKEN)