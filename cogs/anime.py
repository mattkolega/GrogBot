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
                    embed.title = animeData["data"]["Media"]["title"]["english"]
                    embed.url = animeData["data"]["Media"]["siteUrl"]

                    description = animeData["data"]["Media"]["description"]
                    
                    escapeSequences = ''.join(chr(char) for char in range(1, 32))
                    translator = str.maketrans('', '', escapeSequences)
                    description = description.translate(translator)  # Remove escape sequences from description string
                    description = markdownify.markdownify(description)  # Convert HTML tags to markdown

                    embed.description = description

                    embed.set_thumbnail(url=animeData["data"]["Media"]["coverImage"]["large"])

                    color = animeData["data"]["Media"]["coverImage"]["color"]

                    if color != None:
                        color = color.replace("#", "")
                        embed.color = int(color, 16)  # Convert string to hex code

                    embed.add_field(name="Status", value=animeData["data"]["Media"]["status"], inline=True)
                    embed.add_field(name="Episodes", value=animeData["data"]["Media"]["episodes"], inline=True)

                    duration = str(animeData["data"]["Media"]["duration"])

                    if int(duration) == 1:
                        duration += " min"
                    else:
                        duration += " mins"

                    embed.add_field(name="Duration", value=duration, inline=True)

                    embed.add_field(name="Format", value=animeData["data"]["Media"]["format"])

                    genres = ', '.join(str(genre) for genre in animeData["data"]["Media"]["genres"])  # Join list into single string
                    embed.add_field(name="Genres", value=genres, inline=True)

                    embed.add_field(name="Average User Score", value=animeData["data"]["Media"]["averageScore"], inline=True)

                    await ctx.send(embed=embed)

                elif request.status == 404:
                    await ctx.send("Invalid search. I couldn't find anything that matched the search query!")

                else:
                    await ctx.send("Command failed. Please try again later.")

    @commands.command(aliases=["ms"])
    async def mangasearch(self, ctx, *args):
        """Search for a manga in the AniList database"""
        pass

async def setup(bot):
    await bot.add_cog(Anime(bot))