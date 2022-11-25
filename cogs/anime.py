import aiohttp
import discord
import markdownify

from discord.ext import commands

class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Anime cog has successfully loaded")
    
    @commands.command(aliases=["as"])
    async def animesearch(self, ctx, *args):
        """Search for an anime in the AniList database"""
        query = """
        query ($search: String) {
            Media (search: $search, type: ANIME) {
                title {
                    english
                    romaji
                }
                format
                status
                description
                episodes
                duration
                averageScore
                coverImage {
                    large
                    color
                }
                genres
                siteUrl
            }
        }
        """
        
        searchQuery = (" ".join(args))

        queryVariables = {
            "search": searchQuery
        }

        url = "https://graphql.anilist.co"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"query": query, "variables": queryVariables}) as request:
                if request.status == 200:
                    animeData = await request.json()

                    embed = discord.Embed()

                    title = animeData["data"]["Media"]["title"]["english"]

                    if title == None:
                        title = animeData["data"]["Media"]["title"]["romaji"]

                    embed.title = title
                    embed.url = animeData["data"]["Media"]["siteUrl"]

                    description = animeData["data"]["Media"]["description"]

                    if description != None:
                        escapeSequences = ''.join(chr(char) for char in range(1, 32))
                        translator = str.maketrans('', '', escapeSequences)
                        description = description.translate(translator)  # Remove escape sequences from description string
                        description = markdownify.markdownify(description)  # Convert HTML tags to markdown
                        embed.description = description

                    thumbnail = animeData["data"]["Media"]["coverImage"]["large"]

                    if thumbnail != None:
                        embed.set_thumbnail(url=thumbnail) 

                    color = animeData["data"]["Media"]["coverImage"]["color"]

                    if color != None:
                        color = color.replace("#", "")
                        embed.color = int(color, 16)  # Convert string to hex code

                    # -- Status Field --

                    embed.add_field(name="Status", value=animeData["data"]["Media"]["status"], inline=True)

                    # -- Episodes Field --

                    episodes = animeData["data"]["Media"]["episodes"]

                    if episodes == None:
                        episodes = "n/a"

                    embed.add_field(name="Episodes", value=episodes, inline=True)

                    # -- Duration Field --

                    duration = animeData["data"]["Media"]["duration"]

                    if duration == None:
                        duration = "n/a"
                    else:
                        if duration == 1:
                            duration = str(duration) + " min"
                        else:
                            duration = str(duration) + " mins"

                    embed.add_field(name="Duration", value=duration, inline=True)

                    # -- Format Field --

                    format = animeData["data"]["Media"]["format"]

                    if format == None:
                        format = "n/a"
                    
                    embed.add_field(name="Format", value=format, inline=True)

                    # -- Genres Field --

                    genres = animeData["data"]["Media"]["genres"]

                    if not genres:
                        genres = "n/a"
                    else:
                        genres = ', '.join(str(genre) for genre in genres)  # Join list into single string
                    
                    embed.add_field(name="Genres", value=genres, inline=True)

                    # -- Average User Score Field --

                    averageScore = animeData["data"]["Media"]["averageScore"]

                    if averageScore == None:
                        averageScore = "n/a"

                    embed.add_field(name="Average User Score", value=averageScore, inline=True)


                    await ctx.send(embed=embed)

                elif request.status == 404:
                    await ctx.send("Invalid search. I couldn't find anything that matched the search query!")

                else:
                    await ctx.send("Command failed. Please try again later.")

    @commands.command(aliases=["ms"])
    async def mangasearch(self, ctx, *args):
        """Search for a manga in the AniList database"""
        query = """
        query ($search: String) {
            Media (search: $search, type: MANGA) {
                title {
                    english
                    romaji
                }
                format
                status
                description
                chapters
                volumes
                averageScore
                coverImage {
                    large
                    color
                }
                genres
                siteUrl
            }
        }
        """

        searchQuery = (" ".join(args))

        queryVariables = {
            "search": searchQuery
        }

        url = "https://graphql.anilist.co"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"query": query, "variables": queryVariables}) as request:
                if request.status == 200:
                    mangaData = await request.json()

                    embed = discord.Embed()

                    title = mangaData["data"]["Media"]["title"]["english"]

                    if title == None:
                        title = mangaData["data"]["Media"]["title"]["romaji"]

                    embed.title = title
                    embed.url = mangaData["data"]["Media"]["siteUrl"]

                    description = mangaData["data"]["Media"]["description"]

                    if description != None:
                        escapeSequences = ''.join(chr(char) for char in range(1, 32))
                        translator = str.maketrans('', '', escapeSequences)
                        description = description.translate(translator)  # Remove escape sequences from description string
                        description = markdownify.markdownify(description)  # Convert HTML tags to markdown
                        embed.description = description

                    thumbnail = mangaData["data"]["Media"]["coverImage"]["large"]

                    if thumbnail != None:
                        embed.set_thumbnail(url=thumbnail) 

                    color = mangaData["data"]["Media"]["coverImage"]["color"]

                    if color != None:
                        color = color.replace("#", "")
                        embed.color = int(color, 16)  # Convert string to hex code

                    # -- Status Field --

                    embed.add_field(name="Status", value=mangaData["data"]["Media"]["status"], inline=True)

                    # -- Format Field

                    format = mangaData["data"]["Media"]["format"]

                    if format == None:
                        format = "n/a"
                    
                    embed.add_field(name="Format", value=format, inline=True)

                    # -- Average User Score Field -- 

                    averageScore = mangaData["data"]["Media"]["averageScore"]

                    if averageScore == None:
                        averageScore = "n/a"

                    embed.add_field(name="Average User Score", value=averageScore, inline=True)

                    # -- Chapters Field --         
                    
                    chapters = mangaData["data"]["Media"]["chapters"]

                    if chapters == None:
                        chapters = "n/a"

                    embed.add_field(name="Chapters", value=chapters)

                    # -- Volumes Field --

                    volumes = mangaData["data"]["Media"]["volumes"]

                    if volumes == None:
                        volumes = "n/a"

                    embed.add_field(name="Volumes", value=volumes, inline=True)

                    # -- Genres Field --

                    genres = mangaData["data"]["Media"]["genres"]

                    if not genres:
                        genres = "n/a"
                    else:
                        genres = ', '.join(str(genre) for genre in genres)  # Join list into single string
                    
                    embed.add_field(name="Genres", value=genres, inline=True)


                    await ctx.send(embed=embed)

                elif request.status == 404:
                    await ctx.send("Invalid search. I couldn't find anything that matched the search query!")

                else:
                    await ctx.send("Command failed. Please try again later.")

async def setup(bot):
    await bot.add_cog(Anime(bot))