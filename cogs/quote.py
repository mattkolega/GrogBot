import discord
from discord.ext import commands

import datetime
import random
from zoneinfo import ZoneInfo

class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Quote cog has successfully loaded")

    @commands.command()
    async def randomquote(self, ctx):
        """Grabs a random quote from the quotes channel"""
        channel = discord.utils.get(self.bot.get_all_channels(), name="quotes")
        messages = [message async for message in channel.history(limit=500)]
        
        randomQuote = random.choice(messages)

        embed = discord.Embed(title="Random Quote")
        embed.description = randomQuote.content
        embed.url = randomQuote.jump_url
        embed.timestamp = randomQuote.created_at

        if len(randomQuote.attachments) > 0:
                embed.set_image(url=randomQuote.attachments[0].url)

        await ctx.send(embed=embed)

    @commands.command()
    async def quoteofthemonth(self, ctx):
        """Displays the quote with the highest reaction count from the previous month"""
        channel = discord.utils.get(self.bot.get_all_channels(), name="quotes")
        messages = []

        todayutc = datetime.datetime.now()
        localtz = ZoneInfo("Australia/Sydney")
        todaylocal = todayutc.astimezone(localtz) # Convert current UTC time to local time

        beforeDate = datetime.datetime(2022, todaylocal.month, 1, hour=0, minute=0, second=0)
        afterDate = datetime.datetime(2022, todaylocal.month-1, 1, hour=0, minute=0, second=0)

        async for message in channel.history(before=beforeDate, after=afterDate):
            if len(message.reactions) > 0: # Only get messages with reactions
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
            if self.getTotalReactionCount(message) > self.getTotalReactionCount(quoteofthemonth[0]):
                quoteofthemonth.clear()
                quoteofthemonth.append(message)
            elif self.getTotalReactionCount(message) == self.getTotalReactionCount(quoteofthemonth[0]):
                quoteofthemonth.append(message)
        
        if len(quoteofthemonth) > 1:
            await ctx.send("There are multiple Quotes of the Month!")

        for quote in quoteofthemonth:
            embed = discord.Embed(title="Quote of the Month")
            embed.description = quote.content
            embed.url = quote.jump_url
            embed.timestamp = quote.created_at

            if len(quote.attachments) > 0:
                embed.set_image(url=quote.attachments[0].url)

            await ctx.send(embed=embed)

    def getTotalReactionCount(self, message: discord.Message) -> int:
        """Calculates the total number of reactions for a message"""
        messageReactions = message.reactions
        totalReactionCount = 0

        for reaction in messageReactions:
            totalReactionCount += reaction.count
        
        return totalReactionCount

async def setup(bot):
    await bot.add_cog(Quote(bot))