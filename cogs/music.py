import discord
from discord.ext import commands

import asyncio
import youtube_dl

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

class YTDLSource(discord.PCMVolumeTransformer):
    ytdl_format_options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
    }

    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()

        data = await loop.run_in_executor(None, lambda: cls.ytdl.extract_info(url, download=not stream))

        if data is None:
            print("Couldn't find video")

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else cls.ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **cls.ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music cog has successfully loaded")
    
    @commands.command()
    async def joinvoice(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("Couldn't join voice. User is not in a voice channel!")
            return

        channel = ctx.message.author.voice.channel
        
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        
        await channel.connect()
    
    @commands.command()
    async def play(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send("https://tenor.com/view/pelado-re-loco-ruso-crazy-dance-party-drunk-gif-16831286") # Send party gif

        embed = discord.Embed(title="Now Playing :headphones:")
        embed.colour = 0x00ffe3
        embed.description = (f'[{player.title}]({player.url})')
        embed.set_thumbnail(url=player.thumbnail)

        if ctx.message.author.nick:
            embed.set_footer(text=f"Requested by {ctx.message.author.nick}",icon_url=ctx.message.author.avatar.url)
        else:
            embed.set_footer(text=f"Requested by {ctx.message.author.name}",icon_url=ctx.message.author.avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def leavevoice(self, ctx):
        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
    
async def setup(bot):
    await bot.add_cog(Music(bot))