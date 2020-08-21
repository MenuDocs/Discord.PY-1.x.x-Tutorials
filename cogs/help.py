import re
import math
import random

import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        name='help', aliases=['h', 'commands'], description="The help command!"
    )
    async def help(self, ctx, cog="1"):
        helpEmbed = discord.Embed(
            title="Help commands!", color=random.choice(self.bot.color_list)
        )
        helpEmbed.set_thumbnail(url=ctx.author.avatar_url)

        # Get a list of all our current cogs & rmeove ones without commands
        cogs = [c for c in self.bot.cogs.keys()]
        cogs.remove('Events')

        totalPages = math.ceil(len(cogs) / 4)

        if re.search(r"\d", str(cog)):
            cog = int(cog)
            if cog > totalPages or cog < 1:
                await ctx.send(f"Invalid page number: `{cog}`. Please pick from {totalPages} pages.\nAlternatively, simply run `help` to see the first help page.")
                return

            helpEmbed.set_footer(
                text=f"<> - Required & [] - Optional | Page {cog} of {totalPages}"
            )

            neededCogs = []
            for i in range(4):
                x = i + (int(cog) - 1) * 4
                try:
                    neededCogs.append(cogs[x])
                except IndexError:
                    pass

            for cog in neededCogs:
                commandList = ""
                for command in self.bot.get_cog(cog).walk_commands():
                    if command.hidden:
                        continue

                    elif command.parent != None:
                        continue

                    commandList += f"**{command.name}** - *{command.description}*\n"
                commandList += "\n"

                helpEmbed.add_field(name=cog, value=commandList, inline=False)

        elif re.search(r"[a-zA-Z]", str(cog)):
            lowerCogs = [c.lower() for c in cogs]
            if cog.lower() not in lowerCogs:
                await ctx.send(f"Invalid argument: `{cog}`. Please pick from {totalPages} pages.\nAlternatively, simply run `help` to see page one or type `help [category]` to see that categories help command!")
                return

            helpEmbed.set_footer(
                text=f"<> - Required & [] - Optional | Cog {(lowerCogs.index(cog.lower())+1)} of {len(lowerCogs)}"
            )

            helpText = ""

            for command in self.bot.get_cog(cogs[lowerCogs.index(cog.lower())]).walk_commands():
                if command.hidden:
                    continue

                elif command.parent != None:
                    continue

                helpText += f"```{command.name}```\n**{command.description}**\n\n"

                if len(command.aliases) > 0:
                    helpText += f'**Aliases: ** `{", ".join(command.aliases)}`'
                helpText += '\n'

                data = await self.bot.config._Document__get_raw(ctx.guild.id)
                if not data or "prefix" not in data:
                    prefix = self.bot.DEFAULTPREFIX
                else:
                    prefix = data['prefix']

                helpText += f'**Format:** `{prefix}{command.name} {command.usage if command.usage is not None else ""}`\n\n'
            helpEmbed.description = helpText

        else:
            await ctx.send(f"Invalid argument: `{cog}`\nPlease pick from {totalPages} pages.\nAlternatively, simply run `help` to see page one or type `help [category]` to see that categories help command!")
            return

        await ctx.send(embed=helpEmbed)




def setup(bot):
    bot.add_cog(Help(bot))
