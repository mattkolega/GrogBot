import discord
from discord.ext import commands

from dotenv import load_dotenv
from os import environ

import asyncio
import datetime
import random

load_dotenv()
TOKEN = environ["BOT_TOKEN"]
PLAYLIST = environ["PLAYLIST_URL"]

description = "GrogBot. Built using discord.py"
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="$", description=description, intents=intents)
bot.activity = discord.Activity(type=discord.ActivityType.listening, name="Get on the Beers")

initialExtensions = [
    "cogs.fun"
]   

@bot.event
async def on_ready():
    """Executes when the bot has finished starting up"""
    print("We have logged in as {0.user}".format(bot))

@bot.command()
async def hello(ctx):
    """Responds to the user"""
    await ctx.send("G'day!")

@bot.command()
async def randomquote(ctx):
    """Grabs a random quote from the quotes channel"""
    channel = discord.utils.get(bot.get_all_channels(), name="quotes")
    messages = [message async for message in channel.history(limit=500)]
    
    randomIndex = random.randrange(0, len(messages))
    randomQuote = messages[randomIndex]

    embed = discord.Embed(title="Random Quote")
    embed.description = randomQuote.content
    embed.url = randomQuote.jump_url

    if len(randomQuote.attachments) > 0:
            embed.set_image(url=randomQuote.attachments[0].url)

    await ctx.send(embed=embed)

@bot.command()
async def quoteofthemonth(ctx):
    """Displays the quote with the highest reaction count from the previous month"""
    channel = discord.utils.get(bot.get_all_channels(), name="quotes")
    messages = []

    today = datetime.datetime.now()
    beforeDate = datetime.datetime(2022, today.month, 1, hour=0, minute=0, second=0)
    afterDate = datetime.datetime(2022, today.month-1, 1, hour=0, minute=0, second=0)

    async for message in channel.history(before=beforeDate, after=afterDate):
        if len(message.reactions) > 0: 
            messages.append(message)

    if len(messages) == 0:
        await ctx.send("I couldn't find a quote of the month")
        return

    quoteofthemonth = []
    quoteofthemonth.append(messages[0])

    for message in messages:
        if message == quoteofthemonth[0]:
            # Skip to the next item in the messages list to avoid duplicate copy of the first message
            continue
        if getTotalReactionCount(message) > getTotalReactionCount(quoteofthemonth[0]):
            quoteofthemonth.clear()
            quoteofthemonth.append(message)
        elif getTotalReactionCount(message) == getTotalReactionCount(quoteofthemonth[0]):
            quoteofthemonth.append(message)
    
    if len(quoteofthemonth) > 1:
        await ctx.send("There are multiple Quotes of the Month!")

    for quote in quoteofthemonth:
        embed = discord.Embed(title="Quote of the Month")
        embed.description = quote.content
        embed.url = quote.jump_url

        if len(quote.attachments) > 0:
            embed.set_image(url=quote.attachments[0].url)

        await ctx.send(embed=embed)

def getTotalReactionCount(message: discord.Message) -> int:
    """Calculates the total number of reactions for a message"""
    messageReactions = message.reactions
    totalReactionCount = 0

    for reaction in messageReactions:
        totalReactionCount += reaction.count
    
    return totalReactionCount

@bot.command()
async def grogsongs(ctx):
    """Sends playlist link containing party songs"""
    await ctx.send(PLAYLIST)

async def loadExtensions():
    for extension in initialExtensions:
        await bot.load_extension(extension)

async def main():
    async with bot:
        await loadExtensions()
        await bot.start(TOKEN)

asyncio.run(main())