embed = discord.Embed(
    title="this *supports* a **subset** of ~~R Markdown~~",
    color=discord.Colour(0x3b12ef),
    url="https://discordapp.com",
    description="this supports [named links](https://discordapp.com) on top of the subset of markdown.\nYou can use newlines too!",
    timestamp=datetime.datetime.utcfromtimestamp(1580842764) # or any other datetime type format.
)
embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/1.png")
embed.set_author(
    name="author name",
    url="https://discordapp.com",
    icon_url="https://cdn.discordapp.com/embed/avatars/2.png"
)
embed.set_footer(
    text="footer text",
    icon_url="https://cdn.discordapp.com/embed/avatars/3.png"
)

embed.add_field(
    name="footer title",
    value="some of these properties have different limits."
)
embed.add_field(
    name="another footer title",
    value="try exceeding some of them! (coz idk them)"
)
embed.add_field(
    name=":thinking: this supports emotes! (and custom ones too)",
    value="if you exceed them, the error will tell you which value exceeds it."
)
embed.add_field(
    name="Inline",
    value="these last two fields",
    inline=True
)
embed.add_field(
    name="Fields",
    value="are inline fields",
    inline=True
)

await ctx.send(
    content="This is a normal message to be sent alongside the embed",
    embed=embed
)

If you want to send a local file as the embed image:
embed = discord.Embed()
embed.set_image(
    url="attachment://hello.png"
)
image = discord.File("hello.png")
await ctx.send(
    embed=embed
    file=image
)
