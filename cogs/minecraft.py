import io

import aiohttp
import discord

from discord.ext import commands

class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Minecraft cog has successfully loaded")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("Command failed! Minecraft username is required as a command argument.")

    async def getuuid(self, username: str) -> str:
        """Get Minecraft UUID from username"""
        url = f"https://api.mojang.com/users/profiles/minecraft/{username}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as request:
                if request.status == 200:
                    data = await request.json()
                    return data["id"]
        
    @commands.command()
    async def getskin(self, ctx, username: str):
        """Grabs a downloadable copy of a Minecraft skin"""
        uuid = await self.getuuid(username)

        url = f"https://crafatar.com/skins/{uuid}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as request:
                if request.status == 200:
                    data = io.BytesIO(await request.read())
                    await ctx.send(file=discord.File(data, f"{username}_skin.png"))

                else:
                    await ctx.send("Command failed! Failed to download minecraft skin.")
                
    @commands.command()
    async def getskinpreview(self, ctx, username: str):
        """Grabs a rendered preview of a Minecraft skin"""
        uuid = await self.getuuid(username)

        url = f"https://crafatar.com/renders/body/{uuid}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as request:
                if request.status == 200:
                    data = io.BytesIO(await request.read())
                    await ctx.send(file=discord.File(data, f"{username}_skinpreview.png"))
                    
                else:
                    await ctx.send("Command failed! Failed to download minecraft skin preview.")

async def setup(bot):
    await bot.add_cog(Minecraft(bot))