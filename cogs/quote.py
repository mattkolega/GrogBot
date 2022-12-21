import datetime
import random
import traceback
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands

class Quote(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Quote cog has successfully loaded")

    @commands.command()
    async def randomquote(self, ctx: commands.Context):
        """Grabs a random quote from the quotes channel"""
        channel = discord.utils.get(ctx.guild.text_channels, name="quotes")

        if not channel:
            await ctx.send("Command failed. Quotes channel doesn't exist!")
            return

        messages = [message async for message in channel.history(limit=500)]

        if not messages:
            await ctx.send("Command failed. Could not find a quote!")
            return

        randomQuote = random.choice(messages)

        embed = await self.createEmbed(randomQuote)
        await ctx.send(embed=embed)

    @commands.command()
    async def quoteofthemonth(self, ctx: commands.Context):
        """Displays the quote with the highest reaction count from the previous month"""
        channel = discord.utils.get(ctx.guild.text_channels, name="quotes")

        if not channel:
            await ctx.send("Command failed! Quotes channel doesn't exist.")
            return

        localtz = ZoneInfo("Australia/Sydney")
        currentTime = datetime.datetime.now(tz=localtz)

        previousMonth = currentTime.month
        year = currentTime.year

        # Ensure that month doesn't go outside of 1-12 limit
        if (previousMonth - 1) < 1:
            previousMonth = 12
            year -= 1
        else:
            previousMonth -= 1

        collection = self.bot.databaseClient["GrogBot"]["quoteOfTheMonth"]

        numberOfQuotes = await collection.count_documents({"date": {"month": previousMonth, "year": year}})

        if numberOfQuotes > 0:
            if numberOfQuotes > 1:
                await ctx.send("There were multiple Quotes of the Month!")
            
            cursor = collection.find({"date": {"month": previousMonth, "year": year}})

            for document in await cursor.to_list(length=30):
                message = await channel.fetch_message(document["messageID"])

                if not message:
                    await ctx.send(f"Could not find message with ID: {document['messageID']}")
                    continue

                embed = await self.createEmbed(message)
                await ctx.send(embed=embed)

        elif numberOfQuotes == 0:
            quoteOfTheMonth = await self.getQuotesFromChannel(channel, previousMonth, year)

            if not quoteOfTheMonth:
                await ctx.send("Command failed! No quotes were found for previous month.")
                return

            for quote in quoteOfTheMonth:
                document = {"messageID": f"{quote.id}",
                            "date": {"month": previousMonth, "year": year}}

                await collection.insert_one(document)
                
                embed = await self.createEmbed(quote)
                await ctx.send(embed=embed)
    
    @commands.command()
    async def previousquoteofthemonth(self, ctx: commands.Context, date: str):
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

        if numberOfQuotes > 0:
            if numberOfQuotes > 1:
                await ctx.send("There were multiple Quotes of the Month!")
            
            cursor = collection.find({"date": {"month": month, "year": year}})

            for document in await cursor.to_list(length=30):
                message = await channel.fetch_message(document["messageID"])

                if not message:
                    await ctx.send(f"Could not find message with ID: {document['messageID']}")
                    continue

                embed = await self.createEmbed(message)
                await ctx.send(embed=embed)

        elif numberOfQuotes == 0:
            quoteOfTheMonth = await self.getQuotesFromChannel(channel, month, year)

            if not quoteOfTheMonth:
                await ctx.send("Command failed. No quotes were found for the given month!")
                return

            for quote in quoteOfTheMonth:
                document = {"messageID": f"{quote.id}",
                            "date": {"month": month, "year": year}}

                await collection.insert_one(document)
                
                embed = await self.createEmbed(quote)
                await ctx.send(embed=embed)

    async def getQuotesFromChannel(self, channel: discord.TextChannel, month: int, year: int) -> list[discord.Message]:
        """Grabs quote of the month from quotes channel"""
        beforeDateMonth = month
        beforeDateYear = year

        if (beforeDateMonth + 1) > 12:  # Ensure that month doesn't go outside of 1-12 limit
            beforeDateMonth = 1
            beforeDateYear += 1
        else:
            beforeDateMonth += 1

        afterDateMonth = month
        afterDateYear = year

        localtz = ZoneInfo("Australia/Sydney")

        beforeDate = datetime.datetime(beforeDateYear, beforeDateMonth, 1, hour=0, minute=0, second=0, tzinfo=localtz)
        afterDate = datetime.datetime(afterDateYear, afterDateMonth, 1, hour=0, minute=0, second=0, tzinfo=localtz)

        quotes = [message async for message in channel.history(before=beforeDate, after=afterDate) if len(message.reactions) > 0]  # Only get quotes with reactions

        quoteOfTheMonth = []

        if len(quotes) == 0:
            quotes = [message async for message in channel.history(before=beforeDate, after=afterDate)]  # Get all quotes within the single month

            if not quotes:
                return quotes
            
            quoteOfTheMonth.append(random.choice(quotes))  # Randomly pick a quote from the quotes channel if there are no quotes containing reactions
        
        elif len(quotes) > 0:
            quoteOfTheMonth.append(quotes[0])

            for quote in quotes:
                if quote == quoteOfTheMonth[0]:
                    # Skip to the next item in the quoteOfTheMonth list to avoid duplicate copy of the first quote
                    continue
                if await self.getVoteCount(quote) > await self.getVoteCount(quoteOfTheMonth[0]):
                    quoteOfTheMonth.clear()
                    quoteOfTheMonth.append(quote)
                elif await self.getVoteCount(quote) == await self.getVoteCount(quoteOfTheMonth[0]):
                    quoteOfTheMonth.append(quote)
        
        return quoteOfTheMonth
     
    async def getVoteCount(self, message: discord.Message) -> int:
        """Calculates the total number of votes for a quote"""
        userList = []

        for reaction in message.reactions:
            users = [user async for user in reaction.users()]
            userList.extend([user for user in users if user not in userList])  # Add reaction user to userList if not already in userList
        
        return len(userList)  # Calculate length of userList to get total number of votes for a quote
    
    async def createEmbed(self, message: discord.Message) -> discord.Embed:
        """Creates a Quote embed based on a message"""
        embed = discord.Embed(
            title="Quote of the Month",
            description=message.content,
            url=message.jump_url,
            timestamp=message.created_at
        )

        if len(message.attachments) > 0:
            if "image" in message.attachments[0].content_type:
                embed.set_image(url=message.attachments[0].url)
            elif "video" in message.attachments[0].content_type:
                embed.set_footer(text="Quote contains video which can't be displayed in embed.")

        return embed

async def setup(bot: commands.Bot):
    await bot.add_cog(Quote(bot))