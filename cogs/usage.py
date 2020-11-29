import random

import discord
from discord.ext import commands

from utils.util import Pag


class Usage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.qualified_name == "logout":
            return

        if await self.bot.command_usage.find(ctx.command.qualified_name) is None:
            await self.bot.command_usage.upsert(
                {"_id": ctx.command.qualified_name, "usage_count": 1}
            )
        else:
            await self.bot.command_usage.increment(
                ctx.command.qualified_name, 1, "usage_count"
            )

    @commands.command(
        name="commandstats",
        description="Show an overall usage for each command!"
    )
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def command_stats(self, ctx):
        data = await self.bot.command_usage.get_all()
        command_map = {item["_id"]: item["usage_count"] for item in data}

        # get total commands run
        total_commands_run = sum(command_map.values())

        # Sort by value
        sorted_list = sorted(command_map.items(), key=lambda x: x[1], reverse=True)

        pages = []
        cmd_per_page = 10

        for i in range(0, len(sorted_list), cmd_per_page):
            message = "Command Name: `Usage % | Num of command runs`\n\n"
            next_commands = sorted_list[i: i + cmd_per_page]

            for item in next_commands:
                use_percent = item[1] / total_commands_run
                message += f"**{item[0]}**: `{use_percent: .2%} | Ran {item[1]} times`\n"

            pages.append(message)

        await Pag(title="Command Usage Statistics!", color=0xC9B4F4, entries=pages, length=1).start(ctx)


def setup(bot):
    bot.add_cog(Usage(bot))
