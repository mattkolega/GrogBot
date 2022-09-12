import discord
from discord.ext import commands

import random

import aiohttp
from bs4 import BeautifulSoup

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun cog has successfully loaded")

    @commands.command()
    async def magic8ball(self, ctx, *, args=None):
        """Get life advice"""
        if args == None:
            await ctx.send("Command failed. A question is required!")
            return

        possibleAnswers = [
            "It is certain",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]

        answer = random.choice(possibleAnswers)

        await ctx.send(answer)
    
    @commands.command()
    async def urbandictionary(self, ctx, *args):
        """Displays the urban dictionary meaning for a word"""
        searchQuery = (" ".join(args))

        url = f"https://www.urbandictionary.com/define.php?term={searchQuery}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as request:
                if request.status == 200:
                    definition = await self.bot.loop.run_in_executor(None, self.scrape, await request.text())
                
        embed = discord.Embed(title=searchQuery)
        embed.description = definition
        embed.url = url
        
        await ctx.send(embed=embed)

    def scrape(self, html):
        soup = BeautifulSoup(html, features="html.parser")
        content = soup.find("div",attrs={"class":"meaning"}).text
        return content

async def setup(bot):
    await bot.add_cog(Fun(bot))