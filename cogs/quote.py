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
        channel = discord.utils.get(ctx.guild.text_channels, name="quotes")

        if not channel:
            await ctx.send("Command failed. Quotes channel doesn't exist!")
            return

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
        channel = discord.utils.get(ctx.guild.text_channels, name="quotes")

        if not channel:
            await ctx.send("Command failed. Quotes channel doesn't exist!")
            return

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
            if await self.getTotalVoteCount(message) > await self.getTotalVoteCount(quoteofthemonth[0]):
                quoteofthemonth.clear()
                quoteofthemonth.append(message)
            elif await self.getTotalVoteCount(message) == await self.getTotalVoteCount(quoteofthemonth[0]):
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
    
    @commands.command()
    async def previousquoteofthemonth(self, ctx, date):
        """Grabs quotes of the month from past months"""
        dateList = date.split("-")
        month = int(dateList[0])
        year = int(dateList[1])

        channel = discord.utils.get(ctx.guild.text_channels, name="quotes")

        if not channel:
            await ctx.send("Command failed. Quotes channel doesn't exist!")
            return

        collection = self.bot.databaseClient["GrogBot"]["quoteOfTheMonth"]

        numberOfQuotes = await collection.count_documents({"date": {"month": month, "year": year}})

        if numberOfQuotes > 1:
            await ctx.send("There were multiple Quotes of the Month!")
        elif numberOfQuotes == 0:
            await ctx.send("No quotes were found for the given month and year.")
            return

        cursor = collection.find({"date": {"month": month, "year": year}})

        for document in await cursor.to_list(length=30):
            message = await channel.fetch_message(document["messageID"])

            if not message:
                await ctx.send(f"Could not find message with ID: {document['messageID']}")
                continue

            embed = discord.Embed(title="Quote of the Month")
            embed.description = message.content
            embed.url = message.jump_url
            embed.timestamp = message.created_at

            if len(message.attachments) > 0:
                embed.set_image(url=message.attachments[0].url)

            await ctx.send(embed=embed)
        
    async def getVoteCount(self, message: discord.Message) -> int:
        """Calculates the total number of votes for a message"""
        messageReactions = [reaction async for reaction in message.reactions]
        userList = []

        for reaction in messageReactions:
            users = [user async for user in reaction.users()]
            for user in users:
                if user not in userList:
                    userList.append(user)
        
        return len(userList)

async def setup(bot):
    await bot.add_cog(Quote(bot))