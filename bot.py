# Standard libraries
import contextlib
import io
import os
import logging

# Third party libraries
import textwrap
from traceback import format_exception

import discord
from pathlib import Path
import motor.motor_asyncio
from discord.ext import commands

# Local code
import utils.json_loader
from utils.mongo import Document
from utils.util import clean_code, Pag

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")


async def get_prefix(bot, message):
    # If dms
    if not message.guild:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)

    # noinspection PyBroadException
    try:
        data = await bot.config.find(message.guild.id)

        # Make sure we have a usable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)


intents = discord.Intents.all()  # Help command requires member intents
DEFAULTPREFIX = "!"
secret_file = utils.json_loader.read_json("secrets")
bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    owner_id=271612318947868673,
    help_command=None,
    intents=intents,
)  # change command_prefix='-' to command_prefix=get_prefix for custom prefixes
bot.config_token = secret_file["token"]
bot.connection_url = secret_file["mongo"]

bot.news_api_key = secret_file["news api"]
bot.joke_api_key = secret_file["x-rapidapi-key"]

logging.basicConfig(level=logging.INFO)

bot.DEFAULTPREFIX = DEFAULTPREFIX
bot.blacklisted_users = []
bot.muted_users = {}
bot.cwd = cwd

bot.version = "15"

bot.colors = {
    "WHITE": 0xFFFFFF,
    "AQUA": 0x1ABC9C,
    "GREEN": 0x2ECC71,
    "BLUE": 0x3498DB,
    "PURPLE": 0x9B59B6,
    "LUMINOUS_VIVID_PINK": 0xE91E63,
    "GOLD": 0xF1C40F,
    "ORANGE": 0xE67E22,
    "RED": 0xE74C3C,
    "NAVY": 0x34495E,
    "DARK_AQUA": 0x11806A,
    "DARK_GREEN": 0x1F8B4C,
    "DARK_BLUE": 0x206694,
    "DARK_PURPLE": 0x71368A,
    "DARK_VIVID_PINK": 0xAD1457,
    "DARK_GOLD": 0xC27C0E,
    "DARK_ORANGE": 0xA84300,
    "DARK_RED": 0x992D22,
    "DARK_NAVY": 0x2C3E50,
}
bot.color_list = [c for c in bot.colors.values()]


@bot.event
async def on_ready():
    # On ready, print some details to standard out
    print(
        f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\nMy current prefix is: {bot.DEFAULTPREFIX}\n-----"
    )
    await bot.change_presence(
        activity=discord.Game(name="Cries in Binary | 00111010 00101000")
    )  # This changes the bots 'activity'

    for document in await bot.config.get_all():
        print(document)

    currentMutes = await bot.mutes.get_all()
    for mute in currentMutes:
        bot.muted_users[mute["_id"]] = mute

    print(bot.muted_users)

    print("Initialized Database\n-----")


@bot.event
async def on_message(message):
    # Ignore messages sent by yourself
    if message.author.bot:
        return

    # A way to blacklist users from the bot by not processing commands
    # if the author is in the blacklisted_users list
    if message.author.id in bot.blacklisted_users:
        return

    # Whenever the bot is tagged, respond with its prefix
    if message.content.startswith(f"<@!{bot.user.id}>") and len(message.content) == len(
        f"<@!{bot.user.id}>"
    ):
        data = await bot.config.get_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = bot.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        await message.channel.send(f"My prefix here is `{prefix}`", delete_after=15)

    await bot.process_commands(message)


@bot.command(name="eval", aliases=["exec"])
@commands.is_owner()
async def _eval(ctx, *, code):
    code = clean_code(code)

    local_variables = {
        "discord": discord,
        "commands": commands,
        "bot": bot,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message
    }

    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
            exec(
                f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
            )

            obj = await local_variables["func"]()
            result = f"{stdout.getvalue()}\n-- {obj}\n"
    except Exception as e:
        result = "".join(format_exception(e, e, e.__traceback__))

    pager = Pag(
        timeout=100,
        entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
        length=1,
        prefix="```py\n",
        suffix="```"
    )

    await pager.start(ctx)


if __name__ == "__main__":
    # When running this file, if it is the 'main' file
    # I.E its not being imported from another python file run this
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["menudocs"]
    bot.config = Document(bot.db, "config")
    bot.mutes = Document(bot.db, "mutes")
    bot.invites = Document(bot.db, "invites")
    bot.command_usage = Document(bot.db, "command_usage")
    bot.reaction_roles = Document(bot.db, "reaction_roles")

    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

    bot.run(bot.config_token)
