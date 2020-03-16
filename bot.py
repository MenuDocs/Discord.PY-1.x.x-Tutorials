# Libs
import discord # For discord
from discord.ext import commands # For discord
import json # For interacting with json
from pathlib import Path # For paths
import platform # For stats
import logging
import json

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")

#Defining a few things
secret_file = json.load(open(cwd+'/bot_config/secrets.json'))
bot = commands.Bot(command_prefix='-', case_insensitive=True, owner_id=271612318947868673)
bot.config_token = secret_file['token']
logging.basicConfig(level=logging.INFO)

bot.version = '0.0.4'

bot.blacklisted_users = []

@bot.event
async def on_ready():
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\nMy current prefix is: -\n-----")
    data = read_json("blacklist")
    bot.blacklisted_users = data["blacklistedUsers"]
    await bot.change_presence(activity=discord.Game(name=f"Hi, my names {bot.user.name}.\nUse - to interact with me!")) # This changes the bots 'activity'

@bot.event
async def on_command_error(ctx, error):
    #Ignore these errors
    ignored = (commands.CommandNotFound, commands.UserInputError)
    if isinstance(error, ignored):
        return

    #Begin actual error handling
    if isinstance(error, commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)
        if int(h) is 0 and int(m) is 0:
            await ctx.send(f' You must wait {int(s)} seconds to use this command!')
        elif int(h) is 0 and int(m) is not 0:
            await ctx.send(f' You must wait {int(m)} minutes and {int(s)} seconds to use this command!')
        else:
            await ctx.send(f' You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("Hey! You lack permission to use this command.")
    raise error

@bot.event
async def on_message(message):
    #ignore ourselves
    if message.author.id == bot.user.id:
        return

    #blacklist system
    if message.author.id in bot.blacklisted_users:
        return

    if message.content.lower().startswith("help"):
        await message.channel.send("Hey! Why don't you run the help command with `-help`")

    #await bot.process_commands(message)

@bot.command()
@commands.is_owner()
async def blacklist(ctx, user: discord.Member):
    if ctx.message.author.id == user.id:
        await ctx.send("Hey, you cannot blacklist yourself!")
        return

    bot.blacklisted_users.append(user.id)
    data = read_json("blacklist")
    data["blacklistedUsers"].append(user.id)
    write_json(data, "blacklist")
    await ctx.send(f"Hey, I have blacklisted {user.name} for you.")

@bot.command()
@commands.is_owner()
async def unblacklist(ctx, user: discord.Member):
    bot.blacklisted_users.remove(user.id)
    data = read_json("blacklist")
    data["blacklistedUsers"].remove(user.id)
    write_json(data, "blacklist")
    await ctx.send(f"Hey, I have unblacklisted {user.name} for you.")

@bot.command()
async def stats(ctx):
    """
    A usefull command that displays bot statistics.
    """
    pythonVersion = platform.python_version()
    dpyVersion = discord.__version__
    serverCount = len(bot.guilds)
    memberCount = len(set(bot.get_all_members()))

    embed = discord.Embed(title=f'{bot.user.name} Stats', description='\uFEFF', colour=ctx.author.colour, timestamp=ctx.message.created_at)

    embed.add_field(name='Bot Version:', value=bot.version)
    embed.add_field(name='Python Version:', value=pythonVersion)
    embed.add_field(name='Discord.Py Version', value=dpyVersion)
    embed.add_field(name='Total Guilds:', value=serverCount)
    embed.add_field(name='Total Users:', value=memberCount)
    embed.add_field(name='Bot Developers:', value="<@271612318947868673>")

    embed.set_footer(text=f"Carpe Noctem | {bot.user.name}")
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

    await ctx.send(embed=embed)

@bot.command(aliases=['disconnect', 'close', 'stopbot'])
@commands.is_owner()
async def logout(ctx):
    """
    If the user running the command owns the bot then this will disconnect the bot from discord.
    """
    await ctx.send(f"Hey {ctx.author.mention}, I am now logging out :wave:")
    await bot.logout()

@bot.command()
async def echo(ctx, *, message=None):
    """
    A simple command that repeats the users input back to them.
    """
    message = message or "Please provide the message to be repeated."
    await ctx.message.delete()
    await ctx.send(message)

def read_json(filename):
    with open(f"{cwd}/bot_config/{filename}.json", "r") as file:
        data = json.load(file)
    return data

def write_json(data, filename):
    with open(f"{cwd}/bot_config/{filename}.json", "w") as file:
        json.dump(data, file, indent=4)

bot.run(bot.config_token) # Runs our bot
