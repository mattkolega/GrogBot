import datetime
import random
import re
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands

class Quote(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Quote cog has successfully loaded")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("Command failed! Month and year is required as a command argument.")
        else:
            print(error)

    @commands.command(name="randomquote")
    async def randomQuote(self, ctx: commands.Context):
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

        embed = await self.createEmbed("Random Quote", randomQuote)
        await ctx.send(embed=embed)

    @commands.command(name="quoteofthemonth")
    async def quoteOfTheMonth(self, ctx: commands.Context):
        """Manually call quoteOfTheMonth"""
        await self.quoteOfTheCurrentMonth(ctx)

    async def quoteOfTheCurrentMonth(self, ctx: commands.Context):
        """Displays the quote with the highest reaction count from the previous month"""
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

        await self.findQuoteOfTheMonth(ctx, previousMonth, year)

    @commands.command(name="previousquoteofthemonth")
    async def previousQuoteOfTheMonth(self, ctx: commands.Context, date: str):
        """Grabs quotes of the month from past months"""
        if not await self.argumentIsValid(date):
            await ctx.send("Command failed! Invalid argument. Please ensure that the argument is a valid date formatted as 'MM-YYYY'.")
            return

        dateList = date.split("-")
        month = int(dateList[0])
        year = int(dateList[1])

        localtz = ZoneInfo("Australia/Sydney")
        currentTime = datetime.datetime.now(tz=localtz)

        if month == currentTime.month:  # Prevent user from using current month as argument
            await ctx.send("Command failed! Please wait until next month to get the quote of the current month.")
            return
        
        await self.findQuoteOfTheMonth(ctx, month, year)

    async def argumentIsValid(self, argument: str) -> bool:
        """Check if command argument is valid"""
        regexMatch = re.match("^[0-1][0-9]-[0-9]{4}$", argument)  # Ensure that argument's format is MM-YYYY

        if not regexMatch:
            return False
        
        argumentList = argument.split("-")  # Split full date into month and year
        month = int(argumentList[0])
        year = int(argumentList[1])

        if not 1 <= month <= 12:
            return False
        
        if not 1 <= year <= 9999:
            return False

        return True
    
    async def findQuoteOfTheMonth(self, ctx: commands.Context, month: int, year: int):
        """Look for quote in database or quotes channel"""
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

                embed = await self.createEmbed("Quote Of The Month", message)
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
                
                embed = await self.createEmbed("Quote Of The Month", quote)
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
    
    async def createEmbed(self, title: str, message: discord.Message) -> discord.Embed:
        """Creates a Quote embed based on a message"""
        embed = discord.Embed(
            title=title,
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