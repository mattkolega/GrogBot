import discord
from discord.ext import commands

import random
import requests
from bs4 import BeautifulSoup

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun cog has successfully loaded")

    @commands.command()
    async def magic8ball(self, ctx, arg):
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
        request = requests.get(f"https://www.urbandictionary.com/define.php?term={searchQuery}")

        soup = BeautifulSoup(request.content, features="html.parser")

        embed = discord.Embed(title=searchQuery)
        embed.description = soup.find("div",attrs={"class":"meaning"}).text
        embed.url = request.url

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))