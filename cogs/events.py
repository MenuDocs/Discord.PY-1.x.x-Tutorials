import discord
from discord.ext import commands
import random
import datetime

# In cogs we make our own class
# for d.py which subclasses commands.Cog

class Events(commands.Cog):

        def __init__(self, bot):
            self.bot = bot

        @commands.Cog.listener()
        async def on_ready(self):
            print("Events Cog has been loaded\n-----")

        @commands.Cog.listener()
        async def on_member_join(self, member):
            # On member joins we find a channel called general and if it exists,
            # send an embed welcoming them to our guild
            channel = discord.utils.get(member.guild.text_channels, name='recording')
            if channel:
                embed = discord.Embed(description='Welcome to our guild!', color=random.choice(self.bot.color_list))
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
                embed.timestamp = datetime.datetime.utcnow()

                await channel.send(embed=embed)

        @commands.Cog.listener()
        async def on_member_remove(self, member):
            # On member remove we find a channel called general and if it exists,
            # send an embed saying goodbye from our guild-
            channel = discord.utils.get(member.guild.text_channels, name='recording')
            if channel:
                embed = discord.Embed(description='Goodbye from all of us..', color=random.choice(self.bot.color_list))
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
                embed.timestamp = datetime.datetime.utcnow()

                await channel.send(embed=embed)

        @commands.Cog.listener()
        async def on_command_error(self, ctx, error):
            #Ignore these errors
            ignored = (commands.CommandNotFound, commands.UserInputError)
            if isinstance(error, ignored):
                return

            if isinstance(error, commands.CommandOnCooldown):
                # If the command is currently on cooldown trip this
                m, s = divmod(error.retry_after, 60)
                h, m = divmod(m, 60)
                if int(h) is 0 and int(m) is 0:
                    await ctx.send(f' You must wait {int(s)} seconds to use this command!')
                elif int(h) is 0 and int(m) is not 0:
                    await ctx.send(f' You must wait {int(m)} minutes and {int(s)} seconds to use this command!')
                else:
                    await ctx.send(f' You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!')
            elif isinstance(error, commands.CheckFailure):
                # If the command has failed a check, trip this
                await ctx.send("Hey! You lack permission to use this command.")
            raise error

def setup(bot):
    bot.add_cog(Events(bot))
