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
			data = await self.bot.command_usage.find(ctx.author.id)
			if not data or ctx.command.qualified_name not in data:
				await self.bot.command_usage.upsert(
                {"_id":ctx.author.id, ctx.command.qualified_name: 1}
				)
			else:
				await self.bot.command_usage.increment(
                ctx.author.id, 1, ctx.command.qualified_name
				)

		@commands.command(
			name="commandstats",
			description="Show an overall usage for each command!"
		)
		@commands.cooldown(1, 5, commands.BucketType.guild)
		async def command_stats(self, ctx):
			data = await self.bot.command_usage.find(ctx.author.id)
			command_map = {list(data.keys())[i]: list(data.values())[i] for i in range(len(data))}
			command_map.pop("_id")
			# get total commands run
			total_commands_run = sum(command_map.values())

			# Sort by value
			sorted_list = sorted(command_map.items(), key=lambda x: x[1], reverse=True)

			pages = []
			cmd_per_page = 10

			for i in range(0, len(sorted_list), cmd_per_page):
				message = "Command Name: `Usage % | Num of command used`\n\n"
				next_commands = sorted_list[i: i + cmd_per_page]

				for item in next_commands:
					use_percent = item[1] / total_commands_run
					message += f"**{item[0]}**: `{use_percent: .2%} | Used {item[1]} times`\n"

				pages.append(message)

			await Pag(title="Command Usage Statistics!", color=0xC9B4F4, entries=pages, length=1).start(ctx)


def setup(bot):
    bot.add_cog(Usage(bot))
