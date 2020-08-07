import re
import datetime
from copy import deepcopy

import asyncio
import discord
from discord.ext import commands, tasks
from dateutil.relativedelta import relativedelta

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_task = self.check_current_mutes.start()

    def cog_unload(self):
        self.mute_task.cancel()

    @tasks.loop(minutes=5)
    async def check_current_mutes(self):
        currentTime = datetime.datetime.now()
        mutes = deepcopy(self.bot.muted_users)
        for key, value in mutes.items():
            if value['muteDuration'] is None:
                continue

            unmuteTime = value['mutedAt'] + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                guild = self.bot.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])

                role = discord.utils.get(guild.roles, name="Muted")
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Unmuted: {member.display_name}")

                await self.bot.mutes.delete(member.id)
                try:
                    self.bot.muted_users.pop(member.id)
                except KeyError:
                    pass

    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bot.wait_until_ready()

    @commands.command(
        name='mute',
        description="Mutes a given user for x time!",
        ussage='<user> [time]'
    )
    #@commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, time: TimeConverter=None):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        try:
            if self.bot.muted_users[member.id]:
                await ctx.send("This user is already muted")
                return
        except KeyError:
            pass

        data = {
            '_id': member.id,
            'mutedAt': datetime.datetime.now(),
            'muteDuration': time or None,
            'mutedBy': ctx.author.id,
            'guildId': ctx.guild.id,
        }
        await self.bot.mutes.upsert(data)
        self.bot.muted_users[member.id] = data

        await member.add_roles(role)

        if not time:
            await ctx.send(f"Muted {member.display_name}")
        else:
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            if int(hours):
                await ctx.send(
                    f"Muted {member.display_name} for {hours} hours, {minutes} minutes and {seconds} seconds"
                )
            elif int(minutes):
                await ctx.send(
                    f"Muted {member.display_name} for {minutes} minutes and {seconds} seconds"
                )
            elif int(seconds):
                await ctx.send(f"Muted {member.display_name} for {seconds} seconds")

        if time and time < 300:
            await asyncio.sleep(time)

            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send(f"Unmuted `{member.display_name}`")

            await self.bot.mutes.delete(member.id)
            try:
                self.bot.muted_users.pop(member.id)
            except KeyError:
                pass

    @commands.command(
        name='unmute',
        description="Unmuted a member!",
        usage='<user>'
    )
    #@commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        await self.bot.mutes.delete(member.id)
        try:
            self.bot.muted_users.pop(member.id)
        except KeyError:
            pass

        if role not in member.roles:
            await ctx.send("This member is not muted.")
            return

        await member.remove_roles(role)
        await ctx.send(f"Unmuted `{member.display_name}`")


def setup(bot):
    bot.add_cog(Moderation(bot))
