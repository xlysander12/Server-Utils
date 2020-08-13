import json
import os
import random
from datetime import date
from datetime import datetime

import discord
from discord import Guild
from discord import Member
from discord import Message
from discord import Role
from discord import TextChannel
from discord import User
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
servers = 0


# noinspection PyUnusedLocal
def get_prefixbot(client, message):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


def get_prefix(guild: Guild):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(guild.id)]


def get_adminrole(message):
    with open("admins.json", 'r') as f:
        admins = json.load(f)
    role: Role = discord.utils.get(message.guild.roles, id=admins[str(message.guild.id)])
    return role.id


def get_logschannel(message):
    with open("logs.json") as f:
        channels = json.load(f)
    channel: TextChannel = discord.utils.get(message.guild.text_channels, id=channels[str(message.guild.id)])
    return channel.id


def get_announcementsvalue(message):
    with open("announcements.json") as f:
        guilds = json.load(f)
    value: bool = guilds[str(message.guild.id)]
    return value


def get_globalannouncementsvalue(guild: Guild):
    with open("announcements.json") as f:
        guilds = json.load(f)
    value: bool = guilds[str(guild.id)]
    return value


def get_globallogschannel(guild: Guild):
    with open("logs.json") as f:
        channels = json.load(f)
    channel: TextChannel = discord.utils.get(guild.text_channels, id=channels[str(guild.id)])
    return channel.id


def get_musicchannel(guild: Guild):
    with open("cogs/music.json") as f:
        channels = json.load(f)
    channel: TextChannel = discord.utils.get(guild.text_channels, id=channels[str(guild.id)])
    return channel.id


def has_logs_channel(guild: Guild):
    with open("logs.json") as f:
        channels = json.load(f)
    try:
        if channels[str(guild.id)]:
            return True
        else:
            return False
    except Exception:
        return False


# set funcions
def set_prefix(guild: Guild, prefix):
    with open("prefixes.json") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = prefix

    with open("prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)


def set_adminrole(guild: Guild, *, role: Role):
    with open("admins.json") as f:
        roles = json.load(f)

    roles[str(guild.id)] = role.id

    with open("admins.json", 'w') as f:
        json.dump(roles, f, indent=4)


def set_logschannel(guild: Guild, *, channel: TextChannel):
    with open("logs.json") as f:
        channels = json.load(f)

    channels[str(guild.id)] = channel.id

    with open("logs.json", 'w') as f:
        json.dump(channels, f, indent=4)


def set_musicchannel(guild: Guild, *, channel: TextChannel):
    with open("cogs/music.json") as f:
        channels = json.load(f)
    channels[str(guild.id)] = channel.id

    with open("cogs/music.json", 'w') as f:
        json.dump(channels, f, indent=4)


def set_announcements(guild: Guild, value: str):
    with open("announcements.json") as f:
        guilds = json.load(f)

    if str == 'yes':
        guilds[str(guild.id)] = True
    elif str == 'no':
        guilds[str(guild.id)] = False
    else:
        return

    with open("announcements.json", 'w') as f:
        json.dump(guilds, f, indent=4)


bot = commands.Bot(command_prefix=get_prefixbot)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    i = 0
    for guild in bot.guilds:
        print(f"{guild.name} (id: {guild.id})")
        i = i + 1
        global servers
        servers = i
    print(f"Bot is connected to {i} guilds")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{servers} servers"))
    bot.load_extension('cogs.music')


@bot.event
async def on_guild_join(guild):
    # Prefixes
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '!'

    with open("prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)

    # Admin roles
    with open("admins.json", 'r') as f:
        admins = json.load(f)
    admins[str(guild.id)] = 'admin'

    with open("admins.json", 'w') as f:
        json.dump(admins, f, indent=4)

    # Global announcements
    with open("announcements.json") as f:
        guilds = json.load(f)
    guilds[str(guild.id)] = True

    with open("announcements.json", 'w') as f:
        json.dump(guilds, f, indent=4)

    # Messaging server owner
    embed = discord.Embed(title="Hey, looks like I'm in your server!",
                          description="You're receiving this message because I entered your discord server. I know we "
                                      "will have a ball together!",
                          colour=discord.Colour.green(),
                          inline=False)
    embed.add_field(name="Setup command",
                    value="The setup command is the best way to start our journey. Hop in a private channel in your "
                          "discord server and use it!")
    embed.add_field(name="See the github page",
                    value="I have a github repository with all my code in it. Don't worry, even if you don't know "
                          "anything abount coding there's the documentation there too! If you have any problem or "
                          "want to add a suggestion just open an issue there.",
                    inline=False)
    embed.add_field(name="Link", value="https://github.com/xlysander12/Server-Utils", inline=True)

    embed.set_footer(text=bot.user.display_name)
    embed.set_thumbnail(url=bot.user.avatar_url)

    owner = guild.owner

    channel = await owner.create_dm()
    await channel.send(embed=embed)

    # Changing the presence
    global servers
    servers = servers + 1
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{servers} servers"))

    print(f"The bot was added to the guild {guild.name} (id: {guild.id})")


@bot.event
async def on_guild_remove(guild):
    # Prefixes
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)
    prefixes.pop(str(guild.id))

    with open("prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)

    # Admin roles
    with open("admins.json", 'r') as f:
        admins = json.load(f)
    admins.pop(str(guild.id))

    with open("admins.json", 'w') as f:
        json.dump(admins, f, indent=4)

    # Logs' channel

    haslogs = has_logs_channel(guild)
    if haslogs:
        with open("logs.json") as f:
            channels = json.load(f)
        channels.pop(str(guild.id))

        with open("logs.json", 'w') as f:
            json.dump(channels, f, indent=4)

    # Announcements
    with open("announcements.json") as f:
        guilds = json.load(f)
    guilds.pop(str(guild.id))

    # changing presence
    global servers
    servers = servers - 1
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{servers} servers"))
    print(f"The bot was removed from the guild {guild.name} (id: {guild.id})")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)


@bot.command(name='random', help="Responds with a random number beetween a and b")
async def random_command(ctx, a, b):
    response = random.randint(int(a), int(b))
    await ctx.send(response)


@bot.command(name='roll-dice', help="Rolls a dice")
async def roll_dice(ctx, number_of_dice: int = 2, number_of_sides: int = 6):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


@bot.command(name="create-channel", help="Creates a channel")
async def create_channel(ctx, channel_category, channel_name):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return
    guild = ctx.guild
    existing_category = discord.utils.get(guild.categories, name=channel_category)
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_category:
        await guild.create_category(channel_category)
    if not existing_channel:
        await guild.create_text_channel(channel_name,
                                        category=discord.utils.get(guild.categories, name=channel_category))

        channel: TextChannel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        category: discord.CategoryChannel = discord.utils.get(ctx.guild.categories, name=channel_category)

        fdate = date.today().strftime('%d/%m/%Y')
        now = datetime.now().strftime('%H:%M:%S')

        logsembed = discord.Embed(
            title="Channel created",
            colour=discord.Color.dark_blue()
        )

        logsembed.set_footer(text=f"{ctx.message.author.name} at {now} of {fdate}")
        logsembed.add_field(name="Channel name", value=channel.mention, inline=True)
        logsembed.add_field(name="Category", value=category.name, inline=True)

        logschannel = discord.utils.get(ctx.guild.text_channels, id=get_logschannel(ctx))
        await logschannel.send(embed=logsembed)


@bot.command(name="setup", help="Great to use when the bot first joins a server. Setup everything needed")
@commands.has_permissions(administrator=True)
async def start_setup(ctx):
    """if not ctx.author.id == 285084565469528064:
        creator: User = await bot.fetch_user(285084565469528064)
        await ctx.send(
            f"This is a work in progress, therefore it can't be used except by my BEAUTIFUL creator "
            f"{creator.display_name}")
        return"""
    await ctx.send(f"Lets start the setup... First write what you want the prefix for your server to be")

    def check(m):
        return m.author.id == ctx.author.id

    prefix: Message = await bot.wait_for("message", check=check)
    set_prefix(ctx.message.guild, prefix.content)
    await ctx.send(f"Prefix changed to {prefix.content}... Let's keep going")

    await ctx.send(f"Now, mention the role you want it to be the admin role")
    role: Message = await bot.wait_for("message", check=check)
    rolecontent = role.content
    roleid = rolecontent.replace("<", "").replace("@", "").replace("&", "").replace(">", "")
    introleid = int(roleid)
    actualrole = discord.utils.get(ctx.guild.roles, id=introleid)
    set_adminrole(ctx.message.guild, role=actualrole)
    await ctx.send(f"Admin role changed to {actualrole.mention}... Let's keep going")

    await ctx.send(f"Now, mention the channel you want to the logs to go to")
    logsc: Message = await bot.wait_for("message", check=check)
    logsc_content = logsc.content
    logs_id = logsc_content.replace("<", "").replace("#", "").replace("#", "").replace(">", "")

    actual_logsc = discord.utils.get(ctx.guild.text_channels, id=int(logs_id))
    set_logschannel(ctx.message.guild, channel=actual_logsc)
    await ctx.send(f"Logs channel changed to {actual_logsc.mention}... Let's keep going")

    await ctx.send(f"Now, mention the channel you want to be used for music commands")
    musicc: Message = await bot.wait_for("message", check=check)
    musicc_content = musicc.content
    musicc_id = musicc_content.replace("<", "").replace("#", "").replace("#", "").replace(">", "")

    actual_musicc = discord.utils.get(ctx.guild.text_channels, id=int(musicc_id))
    set_musicchannel(ctx.message.guild, channel=actual_musicc)
    await ctx.send(f"Music channel changed to {actual_musicc.mention}... Let's keep going")

    await ctx.send(f"Do you want to receive announcements about this bot's updates or other stuff? (yes / no)")
    announcements = await bot.wait_for("message", check=check)
    set_announcements(ctx.message.guild, announcements)
    if announcements.content == 'yes':
        await ctx.send(f"Global announcements are now enabled")
    if announcements.content == 'no':
        await ctx.send(f"Global announcements are now disabled")

    await ctx.send(
        f"Configuration finished. Remember you can re-configure anything it by using `{get_prefix(ctx.message.guild)}setup` again or using the respective commands")


"""@bot.command(name="setup", help="Great to use when the bot first joins a server. Setup everything needed")
@commands.has_permissions(administrator=True)
async def start_setup(ctx, prefix: str = None, adminrole: Role = None, logschannel: TextChannel = None,
                      announcements: str = 'yes'):
    if not prefix or not adminrole or not logschannel:
        await ctx.send(f"Please specify all needed arguments")
        return
    set_prefix(ctx.message.guild, prefix)
    await ctx.send(f"Prefix changed to {prefix}... Moving...")

    set_adminrole(ctx.message.guild, role=adminrole)
    await ctx.send(f"Admin role changed to {adminrole.mention}... Moving...")

    set_logschannel(ctx.message.guild, channel=logschannel)
    await ctx.send(f"Logs channel changed to {logschannel.mention}... Moving...")

    set_announcements(ctx.message.guild, announcements)
    if announcements == 'yes':
        await ctx.send(f"Global announcements are now ENABLED")
    elif announcements == 'no':
        await ctx.send(f"Global announcements are now DISABLED")
    else:
        await ctx.send(f"Invalid option in announcements field... Keeping default...")

    await ctx.send(
        f"Configuration finished. You can always change the values by using `{get_prefix(ctx.message.guild)}setup` or using the respective commands")"""


@bot.command(name="changeprefix", help="Choose the prefix for your server")
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, prefix):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open("prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send("Prefix changed to " + prefix)

    fdate = date.today().strftime('%d/%m/%Y')
    now = datetime.now().strftime('%H:%M:%S')

    logsembed = discord.Embed(
        title="Server prefix changed",
        colour=discord.Color.purple()
    )

    logsembed.set_footer(text=f"{ctx.message.author.name} at {now} of {fdate}")
    logsembed.add_field(name="Prefix changed to", value=f'"{prefix}"', inline=True)

    logschannel = discord.utils.get(ctx.guild.text_channels, id=get_logschannel(ctx))
    await logschannel.send(embed=logsembed)


@bot.command(name="changeadminrole", help="Choose the role that can execute admin commands")
@commands.has_guild_permissions(administrator=True)
async def changeadmin(ctx, role: Role):
    with open("admins.json", 'r') as f:
        admins = json.load(f)

    admins[str(ctx.guild.id)] = role.id

    with open("admins.json", 'w') as f:
        json.dump(admins, f, indent=4)

    await ctx.send(f"Admin role changed to {role.mention}")

    fdate = date.today().strftime('%d/%m/%Y')
    now = datetime.now().strftime('%H:%M:%S')

    logsembed = discord.Embed(
        title="Admin role changed",
        colour=discord.Color.red()
    )

    logsembed.set_footer(text=f"{ctx.message.author.name} at {now} of {fdate}")
    logsembed.add_field(name="Role changed to", value=role.mention, inline=True)

    logschannel = discord.utils.get(ctx.guild.text_channels, id=get_logschannel(ctx))
    await logschannel.send(embed=logsembed)


@bot.command(name="changelogschannel", help="Choose in which channel will bot's logs be in")
async def changelogs(ctx, channel: TextChannel):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    with open("logs.json") as f:
        channels = json.load(f)

    channels[str(ctx.guild.id)] = channel.id

    with open("logs.json", 'w') as f:
        json.dump(channels, f, indent=4)

    await ctx.send(f"Logs channel changed to {channel.mention}")


@bot.command(name="changemusicchannel", help="Choose in which channel will be used to execute music commands")
async def changelogs(ctx, channel: TextChannel):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    with open("cogs/music.json") as f:
        channels = json.load(f)

    channels[str(ctx.guild.id)] = channel.id

    with open("cogs/music.json", 'w') as f:
        json.dump(channels, f, indent=4)

    await ctx.send(f"Music channel changed to {channel.mention}")


@bot.command(name="kick", help="Kicks a member from the server")
async def kickmember(ctx, target: Member, *, reason="None"):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    fdate = date.today().strftime('%d/%m/%Y')
    now = datetime.now().strftime('%H:%M:%S')

    invite = await ctx.channel.create_invite()
    channel = await target.create_dm()
    # await channel.send("You have been kicked from the server " + ctx.guild.name)
    # await channel.send("With the following reason: " + reason)
    # await channel.send(f"Kicked by: {ctx.message.author.name}")
    # await channel.send(f"Consider this as an warning... You can re-enter the server here: {invite}")

    clientembed = discord.Embed(
        title="You have been kicked",
        colour=discord.Color.orange()
    )

    clientembed.set_footer(text="Server Utils Bot")
    clientembed.add_field(name='You have been kicked from the server', value=ctx.guild.name, inline=True)
    clientembed.add_field(name='Reason of the kick', value=reason, inline=True)
    clientembed.add_field(name='You were kicked by', value=ctx.message.author.name, inline=False)
    clientembed.add_field(name='Consider yourself warned... You can re-enter here', value=invite, inline=True)
    # await channel.send(f"You have been kicked from the server {ctx.guild.name}\n"
    # f"With the following reason: {reason}\n"
    # f"Kicked by: {ctx.message.author.name}\n"
    # f"Consider this as an warning... You can re-enter the server here: {invite}")

    await channel.send(embed=clientembed)
    await target.kick(reason=reason)

    logsembed = discord.Embed(
        title="A member has been kicked",
        colour=discord.Color.orange()
    )

    logsembed.set_footer(text=f"{ctx.message.author.name} at {now} of {fdate}")
    logsembed.add_field(name="Kicked member", value=target.mention, inline=True)
    logsembed.add_field(name="Reason", value=reason, inline=True)

    logschannel = discord.utils.get(ctx.guild.text_channels, id=get_logschannel(ctx))
    await logschannel.send(embed=logsembed)

    await ctx.send(f"User {target} was kicked from the server")


@bot.command(name='ban', help="Bans a member from the server", category="Administration")
async def banmember(ctx, target: Member, reason='None'):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    fdate = date.today().strftime('%d/%m/%Y')
    now = datetime.now().strftime('%H:%M:%S')

    channel = await target.create_dm()
    clientembed = discord.Embed(
        title="You have been banned",
        colour=discord.Color.red()
    )

    clientembed.set_footer(text="Server Utils Bot")
    clientembed.add_field(name="You have been BANNED from the server", value=ctx.guild.name, inline=False)
    clientembed.add_field(name='Reason of the ban', value=reason, inline=True)
    clientembed.add_field(name="You were banned by", value=ctx.message.author.name, inline=True)

    await channel.send(embed=clientembed)
    await target.ban(reason=reason)
    await ctx.send(f"User {target} was banned from the server")

    logsembed = discord.Embed(
        title="A member has been BANNED",
        colour=discord.Color.orange()
    )

    logsembed.set_footer(text=f"{ctx.message.author.name} at {now} of {fdate}")
    logsembed.add_field(name="Banned member", value=target.mention, inline=True)
    logsembed.add_field(name="Reason", value=reason, inline=True)

    logschannel = discord.utils.get(ctx.guild.text_channels, id=get_logschannel(ctx))
    await logschannel.send(embed=logsembed)


@bot.command(name="clear", help="cleans a certain ammount of messages in the channel")
async def clear_messages(ctx, ammount: int):
    await ctx.message.channel.purge(limit=ammount + 1)


@bot.command(name="globalannouncement",
             help="A command to make announcements in EVERY server the bot is in (Only used by bot's staff members)")
async def global_announcement(ctx, *, message):
    if not ctx.author.id == 285084565469528064:
        creator: User = await bot.fetch_user(285084565469528064)
        await ctx.send(
            f"This is a bot's staff command only... You can't just use it dummy")
        return
    print(f"Global announcement started by {ctx.author.name}. Here comes the spaaaam")
    for guild in bot.guilds:
        if get_globalannouncementsvalue(guild):
            logschannel = discord.utils.get(guild.text_channels, id=get_globallogschannel(guild))
            await logschannel.send(message)
            print(f"Global message sent to {guild.name} (id: {guild.id})")


@bot.command(name="announcements",
             help="Enable or disable bot's announcements in your logs' channel (It can be bots' updates or another "
                  "fun thing... You never know)")
async def set_globalannouncements(ctx):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return
    if get_announcementsvalue(ctx):
        with open("announcements.json") as f:
            guilds = json.load(f)
        guilds[str(ctx.guild.id)] = False

        with open("announcements.json", 'w') as f:
            json.dump(guilds, f, indent=4)
        return
    if not get_announcementsvalue(ctx):
        with open("announcements.json") as f:
            guilds = json.load(f)
        guilds[str(ctx.guild.id)] = True

        with open("announcements.json", 'w') as f:
            json.dump(guilds, f, indent=4)
        return


bot.run(TOKEN)
