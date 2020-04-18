import discord
from discord.ext import commands

class Groups(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("SubCommands Cog has been loaded\n-----")

    @commands.group()
    async def first(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("This is the first command layer")

    @first.group()
    async def second(self, ctx):
        print(ctx.invoked_subcommand)
        if ctx.invoked_subcommand is None:
            await ctx.message.author.send("Hey! Did this come through clearly?")

    @second.command()
    async def third(self, ctx, channelId=None):
        if channelId != None:
            channel = self.bot.get_channel(int(channelId))
            await channel.send("Hey! This is a message from me the bot. Bet you didn't see who ran the command?", delete_after=15)


def setup(bot):
    bot.add_cog(Groups(bot))
