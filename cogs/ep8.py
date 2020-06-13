import discord
from discord.ext import commands

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        A command which kicks a given user
        !kick <member> <Reason=None>
        """
        await ctx.guild.kick(user=member, reason=reason)
        channel = self.bot.get_channel(502990000422387722)
        # Using our past episodes knowledge can we make channel dynamic?
        embed = discord.Embed(title=f"{ctx.author.name} kicked: {member.name}", description=reason)
        await channel.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """
        A command which bans a given user
        !ban <member> <Reason=None>
        """
        await ctx.guild.ban(user=member, reason=reason)
        channel = self.bot.get_channel(502990000422387722)
        # Using our past episodes knowledge can we make channel dynamic?
        embed = discord.Embed(title=f"{ctx.author.name} banned: {member.name}", description=reason)
        await channel.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    #@commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, amount=15):
        """
        A command which purges the channel it is called in
        !purge <amount=15>
        """
        await ctx.channel.purge(limit=amount+1)
        channel = self.bot.get_channel(502990000422387722)
        # Using our past episodes knowledge can we make channel dynamic?
        embed = discord.Embed(title=f"{ctx.author.name} purged: {ctx.channel.name}", description=f"{amount} messages were cleared")
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Moderation(bot))
