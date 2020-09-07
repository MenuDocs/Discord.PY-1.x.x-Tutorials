import discord
from aiohttp import ClientSession
from discord.ext import commands, tasks


class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="dadjoke",
        description="Send a dad joke!",
        aliases=['dadjokes']
    )
    async def dadjoke(self, ctx):
        url = "https://dad-jokes.p.rapidapi.com/random/jokes"

        headers = {
            'x-rapidapi-host': "dad-jokes.p.rapidapi.com",
            'x-rapidapi-key': self.bot.joke_api_key
        }

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                r = await response.json()
                await ctx.send(f"**{r['setup']}**\n\n||{r['punchline']}||")


def setup(bot):
    bot.add_cog(API(bot))
