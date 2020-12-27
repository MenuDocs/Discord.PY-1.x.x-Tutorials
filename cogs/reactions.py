import typing
import discord

import emojis
from discord.ext import commands


class ReactionRolesNotSetup(commands.CommandError):
    """Reaction roles are not setup for this guild."""
    pass


def is_setup():
    async def wrap_func(ctx):
        data = await ctx.bot.config.find(ctx.guild.id)
        if data is None:
            raise ReactionRolesNotSetup

        if data.get("message_id") is None:
            raise ReactionRolesNotSetup

        return True
    return commands.check(wrap_func)


class Reactions(commands.Cog, name="ReactionRoles"):
    def __init__(self, bot):
        self.bot = bot

    async def rebuild_role_embed(self, guild_id):
        data = await self.bot.config.find(guild_id)
        channel_id = data["channel_id"]
        message_id = data["message_id"]

        guild = await self.bot.fetch_guild(guild_id)
        channel = await self.bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)

        embed = discord.Embed(title="Reaction Roles!")
        await message.clear_reactions()

        desc = ""
        reaction_roles = await self.bot.reaction_roles.get_all()
        reaction_roles = list(filter(lambda r: r['guild_id'] == guild_id, reaction_roles))
        for item in reaction_roles:
            role = guild.get_role(item["role"])
            desc += f"{item['_id']}: {role.mention}\n"
            await message.add_reaction(item["_id"])

        embed.description = desc
        await message.edit(embed=embed)

    async def get_current_reactions(self, guild_id):
        data = await self.bot.reaction_roles.get_all()
        data = filter(lambda r: r['guild_id'] == guild_id, data)
        data = map(lambda r: r["_id"], data)
        return list(data)

    @commands.group(
        aliases=['rr'], invoke_without_command=True
    )
    @commands.guild_only()
    async def reactionroles(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), entity="reactionroles")

    @reactionroles.command(name="channel")
    @commands.guild_only()
    #@commands.has_guild_permissions(manage_channels=True)
    async def rr_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the reaction roles channel."""
        if channel is None:
            await ctx.send("You did not give me a channel, therefore I will use the current one!")

        channel = channel or ctx.channel
        try:
            await channel.send("testing if I can send messages here", delete_after=0.05)
        except discord.HTTPException:
            await ctx.send("I cannot send a message to that channel! Please give me perms and try again.", delete_after=30)
            return

        embed = discord.Embed(title="Reaction Roles!")

        desc = ""
        reaction_roles = await self.bot.reaction_roles.get_all()
        reaction_roles = list(filter(lambda r: r['guild_id'] == ctx.guild.id, reaction_roles))
        for item in reaction_roles:
            role = ctx.guild.get_role(item["role"])
            desc += f"{item['_id']}: {role.mention}\n"
        embed.description = desc

        m = await channel.send(embed=embed)
        for item in reaction_roles:
            await m.add_reaction(item["_id"])

        await self.bot.config.upsert(
            {
                "_id": ctx.guild.id,
                "message_id": m.id,
                "channel_id": m.channel.id,
                "is_enabled": True,
            }
        )
        await ctx.send("That should be all setup for you!", delete_after=30)

    @reactionroles.command(name="toggle")
    @commands.guild_only()
    #@commands.has_guild_permissions(administrator=True)
    @is_setup()
    async def rr_toggle(self, ctx):
        """Toggle reaction roles for this guild."""
        data = await self.bot.config.find(ctx.guild.id)
        data["is_enabled"] = not data["is_enabled"]
        await self.bot.config.upsert(data)

        is_enabled = "enabled." if data["is_enabled"] else "disabled."
        await ctx.send(f"I have toggled that for you! It is currently {is_enabled}")

    @reactionroles.command(name="add")
    @commands.guild_only()
    # @commands.has_guild_permissions(manage_roles=True)
    @is_setup()
    async def rr_add(self, ctx, emoji: typing.Union[discord.Emoji, str], *, role: discord.Role):
        """Add a new reaction role."""
        reacts = await self.get_current_reactions(ctx.guild.id)
        if len(reacts) >= 20:
            await ctx.send("This does not support more then 20 reaction roles per guild!")
            return

        if not isinstance(emoji, discord.Emoji):
            emoji = emojis.get(emoji)
            emoji = emoji.pop()

        elif isinstance(emoji, discord.Emoji):
            if not emoji.is_usable():
                await ctx.send("I can't use that emoji")
                return

        emoji = str(emoji)
        await self.bot.reaction_roles.upsert({"_id": emoji, "role": role.id, "guild_id": ctx.guild.id})

        await self.rebuild_role_embed(ctx.guild.id)
        await ctx.send("That is added and good to go!")

    @reactionroles.command(name="remove")
    @commands.guild_only()
    # @commands.has_guild_permissions(manage_roles=True)
    @is_setup()
    async def rr_remove(self, ctx, emoji: typing.Union[discord.Emoji, str]):
        """Remove an existing reaction role"""
        if not isinstance(emoji, discord.Emoji):
            emoji = emojis.get(emoji)
            emoji = emoji.pop()

        emoji = str(emoji)

        await self.bot.reaction_roles.delete(emoji)

        await self.rebuild_role_embed(ctx.guild.id)
        await ctx.send("That should all done and removed for you!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        data = await self.bot.config.find(payload.guild_id)

        if not payload.guild_id or not data or not data.get("is_enabled"):
            return

        guild_reaction_roles = await self.get_current_reactions(payload.guild_id)
        if str(payload.emoji) not in guild_reaction_roles:
            return

        guild = await self.bot.fetch_guild(payload.guild_id)

        emoji_data = await self.bot.reaction_roles.find(str(payload.emoji))
        role = guild.get_role(emoji_data["role"])

        member = await guild.fetch_member(payload.user_id)

        if role not in member.roles:
            await member.add_roles(role, reason="Reaction role.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        data = await self.bot.config.find(payload.guild_id)

        if not payload.guild_id or not data or not data.get("is_enabled"):
            return

        guild_reaction_roles = await self.get_current_reactions(payload.guild_id)
        if str(payload.emoji) not in guild_reaction_roles:
            return

        guild = await self.bot.fetch_guild(payload.guild_id)

        emoji_data = await self.bot.reaction_roles.find(str(payload.emoji))
        role = guild.get_role(emoji_data["role"])

        member = await guild.fetch_member(payload.user_id)

        if role in member.roles:
            await member.remove_roles(role, reason="Reaction role.")


def setup(bot):
    bot.add_cog(Reactions(bot))
