# sys.path.insert(1, 'cogs/')
import asyncio
import os
import random
import sys
from datetime import datetime

import discord
import mysql.connector as mysql
import requests
from discord import Guild
from discord import Member
from discord import Message
from discord import Role
from discord import TextChannel
from discord import User
from discord.ext import commands
from discord.ext.tasks import loop
from dotenv import load_dotenv

from redditbot import reddit

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
servers = 0
in_setup = []
mydb = None
mycursor = None


# Connect to mysql
def connectmysql():
    global mydb
    global mycursor
    try:
        mydb = mysql.connect(
            host="{IP}",
            user="{user}",
            password="{password}",
            database="{db}"
        )
        print(f"Connected to database")
    except mysql.Error:
        sys.exit(f"Couldn't establish connection to mysql server")

    mycursor = mydb.cursor()


# noinspection PyUnusedLocal
@loop(count=None)
async def keep_mysql():
    while True:
        # keepalive = "SELECT * FROM prefixes"
        # mycursor.execute(keepalive)
        # result = mycursor.fetchall()
        # print("Keeping mysql connection alive")
        # await asyncio.sleep(180)
        mycursor.close()
        connectmysql()
        await asyncio.sleep(180)


def get_prefixbot(client, message):
    # with open("prefixes.json", 'r') as f:
    # prefixes = json.load(f)
    # return prefixes[str(message.guild.id)]
    sqlcommand = f"SELECT prefix FROM prefixes WHERE guildid = %s"
    vals = (message.guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    prefix = str(result[0])
    return prefix.replace("(", "").replace(")", "").replace(",", "").replace("'", "")


def get_prefix(guild: Guild):
    sqlcommand = f"SELECT prefix FROM prefixes WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    prefix = str(result[0])
    return prefix.replace("(", "").replace(")", "").replace(",", "").replace("'", "")


def get_adminrole(message):
    # with open("admins.json", 'r') as f:
    # admins = json.load(f)

    sqlcommand = f"SELECT roleid FROM adminroles WHERE guildid = %s"
    vals = (message.guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strroleid = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    roleid = int(strroleid)
    # role: Role = discord.utils.get(message.guild.roles, id=roleid)
    return roleid


def get_logschannel(message):
    # with open("logs.json") as f:
    #     channels = json.load(f)
    # channel: TextChannel = discord.utils.get(message.guild.text_channels, id=channels[str(message.guild.id)])
    sqlcommand = "SELECT channelid FROM logschannels WHERE guildid = %s"
    vals = (message.guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strchannelid = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    channelid = int(strchannelid)
    return channelid


def get_announcementsvalue(message):
    # with open("announcements.json") as f:
    #     guilds = json.load(f)
    # value: bool = guilds[str(message.guild.id)]
    # return value
    sqlcommand = "SELECT value FROM globalannouncementsvalue WHERE guildid = %s"
    vals = (message.guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strresult = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    intresult = int(strresult)
    boolresult = bool(intresult)
    return boolresult


def get_globalannouncementsvalue(guild: Guild):
    # with open("announcements.json") as f:
    #     guilds = json.load(f)
    # value: bool = guilds[str(guild.id)]
    # return value
    sqlcommand = "SELECT value FROM globalannouncementsvalue WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strresult = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    intresult = int(strresult)
    boolresult = bool(intresult)
    return boolresult


def get_musicchannel(guild: Guild):
    sqlcommand = "SELECT channelid FROM musicchannels WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strchannelid = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    channelid = int(strchannelid)
    return channelid


def get_globallogschannel(guild: Guild):
    # with open("logs.json") as f:
    #     channels = json.load(f)
    # channel: TextChannel = discord.utils.get(guild.text_channels, id=channels[str(guild.id)])
    # return channel.id
    sqlcommand = "SELECT channelid FROM logschannels WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strchannelid = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    channelid = int(strchannelid)
    return channelid


# def get_musicchannel(guild: Guild):
#     # with open("cogs/music.json") as f:
#     #     channels = json.load(f)
#     # channel: TextChannel = discord.utils.get(guild.text_channels, id=channels[str(guild.id)])
#     # return channel.id
#     sqlcommand = "SELECT channelid FROM musicchannels WHERE guildid = %s"
#     vals = (guild.id,)
#     mycursor.execute(sqlcommand, vals)
#     result = mycursor.fetchall()
#     return result[0]


def get_defrole(guild: Guild):
    # with open("defaultroles.json") as f:
    #     defroles = json.load(f)
    # defrole: Role = discord.utils.get(guild.roles, id=defroles[str(guild.id)])
    # return defrole.id
    sqlcommand = "SELECT roleid FROM autorole WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strchannelid = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    roleid = int(strchannelid)
    return roleid


def get_autorole(guild: Guild):
    # with open("autorole.json") as f:
    #     autovals = json.load(f)
    # autoval: bool = autovals[str(guild.id)]
    # return autoval
    sqlcommand = "SELECT value FROM autorole WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strresult = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    intresult = int(strresult)
    boolresult = bool(intresult)
    return boolresult


def get_setup(guild: Guild):
    # with open("has_setup.json") as f:
    #     guilds = json.load(f)
    # val = guilds[str(guild.id)]
    # return val
    sqlcommand = "SELECT value FROM has_setup WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strresult = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    intresult = int(strresult)
    boolresult = bool(intresult)
    return boolresult


# def has_logs_channel(guild: Guild):
#     with open("logs.json") as f:
#         channels = json.load(f)
#     try:
#         if channels[str(guild.id)]:
#             return True
#         else:
#             return False
#     except Exception:
#         return False


# set functions
def set_prefix(guild: Guild, prefix):
    # with open("prefixes.json") as f:
    #     prefixes = json.load(f)
    #
    # prefixes[str(guild.id)] = prefix
    #
    # with open("prefixes.json", 'w') as f:
    #     json.dump(prefixes, f, indent=4)
    checksqlcommand = "SELECT * FROM prefixes WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if result:
        sqlcommand = "UPDATE prefixes SET prefix = %s WHERE guildid = %s"
        vals = (prefix, guild.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
        return
    if not result:
        sqlcommand = "INSERT INTO prefixes(guildid, prefix) VALUES (%s, %s)"
        vals = (guild.id, prefix)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
        return


def set_adminrole(guild: Guild, *, role: Role):
    # with open("admins.json") as f:
    #     roles = json.load(f)
    #
    # roles[str(guild.id)] = role.id
    #
    # with open("admins.json", 'w') as f:
    #     json.dump(roles, f, indent=4)

    checksqlcommand = "SELECT * FROM adminroles WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if not result:
        sqlcommand = "INSERT INTO adminroles(guildid, roleid) VALUES (%s, %s)"
        vals = (guild.id, role.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
        return
    if result:
        sqlcommand = "UPDATE adminroles SET roleid = %s WHERE guildid = %s"
        vals = (role.id, guild.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
        return


def set_logschannel(guild: Guild, *, channel: TextChannel):
    # with open("logs.json") as f:
    #     channels = json.load(f)
    #
    # channels[str(guild.id)] = channel.id
    #
    # with open("logs.json", 'w') as f:
    #     json.dump(channels, f, indent=4)
    checksqlcommand = "SELECT * FROM logschannels WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if not result:
        sqlcommand = "INSERT INTO logschannels(guildid, channelid) VALUES (%s, %s)"
        vals = (guild.id, channel.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
        return
    if result:
        sqlcommand = "UPDATE logschannels SET channelid = %s WHERE guildid = %s"
        vals = (channel.id, guild.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
        return


# def set_defrole(guild: Guild, *, role: Role):
#     with open("defaultroles.json") as f:
#         defroles = json.load(f)
#     defroles[str(guild.id)] = role.id
#
#     with open("defaultroles.json", 'w') as f:
#         json.dump(defroles, f, indent=4)


def set_autorole(guild: Guild, val: bool, role: Role = None):
    # with open("autorole.json") as f:
    #     autovals = json.load(f)
    # autovals[str(guild.id)] = val
    #
    # with open("autorole.json", 'w') as f:
    #     json.dump(autovals, f, indent=4)
    checksqlcommand = "SELECT * FROM autorole WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if result:
        if val:
            sqlcommand = "UPDATE autorole SET value = %s, roleid = %s WHERE guildid = %s"
            vals = (1, role.id, guild.id)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
        if not val:
            sqlcommand = "UPDATE autorole SET value = %s WHERE guildid = %s"
            vals = (0, guild.id)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
    if not result:
        if val:
            sqlcommand = "INSERT INTO autorole(guildid, value, roleid) VALUES (%s, %s, %s)"
            vals = (guild.id, 1, role.id)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
        if not val:
            sqlcommand = "INSERT INTO autorole(guildid, value) VALUES (%s, %s)"
            vals = (guild.id, 0)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()


def set_musicchannel(guild: Guild, *, channel: TextChannel):
    # with open("cogs/music.json") as f:
    #     channels = json.load(f)
    # channels[str(guild.id)] = channel.id
    #
    # with open("cogs/music.json", 'w') as f:
    #     json.dump(channels, f, indent=4)
    checksqlcommand = "SELECT * FROM musicchannels WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if result:
        sqlcommand = "UPDATE musicchannels SET channelid = %s WHERE guildid = %s"
        vals = (channel.id, guild.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
    if not result:
        sqlcommand = "INSERT INTO musicchannels(guildid, channelid) VALUES (%s, %s)"
        vals = (guild.id, channel.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()


def set_announcements(guild: Guild, value: str):
    # with open("announcements.json") as f:
    #     guilds = json.load(f)
    #
    # if value == 'yes':
    #     guilds[str(guild.id)] = True
    # elif value == 'no':
    #     guilds[str(guild.id)] = False
    # else:
    #     return
    #
    # with open("announcements.json", 'w') as f:
    #     json.dump(guilds, f, indent=4)
    if value == "yes":
        sqlcommand = "UPDATE globalannouncementsvalue SET value = %s WHERE guildid = %s"
        vals = (1, guild.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
    if value == "no":
        sqlcommand = "UPDATE globalannouncementsvalue SET value = %s WHERE guildid = %s"
        vals = (0, guild.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()


def set_setup(guild: Guild, value: bool):
    # with open("has_setup.json") as f:
    #     guilds = json.load(f)
    # if value:
    #     guilds[str(guild.id)] = True
    # if not value:
    #     guilds[str(guild.id)] = False
    #
    # with open("has_setup.json", 'w') as f:
    #     json.dump(guilds, f, indent=4)
    if value:
        value = 1
    if not value:
        value = 0

    checksqlcommand = "SELECT * FROM has_setup WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if result:
        sqlcommand = "UPDATE has_setup SET value = %s WHERE guildid = %s"
        vals = (value, guild.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
    if not result:
        sqlcommand = "INSERT INTO has_setup(guildid, value) VALUES (%s, %s)"
        vals = (guild.id, value)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()


bot = commands.Bot(command_prefix=get_prefixbot)
# bot = commands.Bot(command_prefix="!")
bot.remove_command('help')


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
    connectmysql()
    keep_mysql.start()


@bot.event
async def on_guild_join(guild):
    # Prefixes
    # with open("prefixes.json", 'r') as f:
    #     prefixes = json.load(f)
    #
    # prefixes[str(guild.id)] = '!'
    #
    # with open("prefixes.json", 'w') as f:
    #     json.dump(prefixes, f, indent=4)

    set_prefix(guild, "!")

    # Admin roles
    # with open("admins.json", 'r') as f:
    #     admins = json.load(f)
    # admins[str(guild.id)] = 'admin'
    #
    # with open("admins.json", 'w') as f:
    #     json.dump(admins, f, indent=4)

    # Global announcements
    # with open("announcements.json") as f:
    #     guilds = json.load(f)
    # guilds[str(guild.id)] = True
    #
    # with open("announcements.json", 'w') as f:
    #     json.dump(guilds, f, indent=4)
    announcementssqlcommand = "INSERT INTO globalannouncementsvalue(guildid, value) VALUES (%s, %s)"
    vals = (guild.id, 1)
    mycursor.execute(announcementssqlcommand, vals)
    mydb.commit()

    # Auto Role
    # with open("autorole.json") as f:
    #     autovals = json.load(f)
    # autovals[str(guild.id)] = False
    # 
    # with open("autorole.json", 'w') as f:
    #     json.dump(autovals, f, indent=4)
    set_autorole(guild, False)

    # Setup check
    # with open("has_setup.json") as f:
    #     setupvals = json.load(f)
    # setupvals[str(guild.id)] = False
    #
    # with open("has_setup.json", 'w') as f:
    #     json.dump(setupvals, f, indent=4)
    set_setup(guild, False)

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
    # with open("prefixes.json", 'r') as f:
    #     prefixes = json.load(f)
    # prefixes.pop(str(guild.id))
    #
    # with open("prefixes.json", 'w') as f:
    #     json.dump(prefixes, f, indent=4)

    prefixsqlcommand = "DELETE FROM prefixes WHERE guildid = %s"
    prefixvals = (guild.id,)
    mycursor.execute(prefixsqlcommand, prefixvals)
    mydb.commit()
    # Admin roles
    # with open("admins.json", 'r') as f:
    #     #     admins = json.load(f)
    #     # admins.pop(str(guild.id))
    #     #
    #     # with open("admins.json", 'w') as f:
    #     #     json.dump(admins, f, indent=4)
    adminsqlcommand = "DELETE FROM adminroles WHERE guildid = %s"
    adminvals = (guild.id,)
    mycursor.execute(adminsqlcommand, adminvals)
    mydb.commit()

    # Logs' channel

    # haslogs = has_logs_channel(guild)
    # if haslogs:
    #     with open("logs.json") as f:
    #         channels = json.load(f)
    #     channels.pop(str(guild.id))
    #
    #     with open("logs.json", 'w') as f:
    #         json.dump(channels, f, indent=4)
    logssqlcommand = "DELETE FROM logschannels WHERE guildid = %s"
    logsvals = (guild.id,)
    mycursor.execute(logssqlcommand, logsvals)
    mydb.commit()

    # Announcements
    # with open("announcements.json") as f:
    #     guilds = json.load(f)
    # guilds.pop(str(guild.id))
    #
    # with open("announcements.json", 'w') as f:
    #     json.dump(guilds, f, indent=4)
    announcementssqlcommand = "DELETE FROM globalannouncementsvalue WHERE guildid = %s"
    announcementsvals = (guild.id,)
    mycursor.execute(announcementssqlcommand, announcementsvals)
    mydb.commit()

    # Auto role
    # with open("autorole.json") as f:
    #     autovals = json.load(f)
    # autovals.pop(str(guild.id))
    #
    # with open("autorole.json", 'w') as f:
    #     json.dump(autovals, f, indent=4)
    autorolesqlcommand = "DELETE FROM autorole WHERE guildid = %s"
    autorolevals = (guild.id,)
    mycursor.execute(autorolesqlcommand, autorolevals)
    mydb.commit()

    # Setup check
    # with open("has_setup.json") as f:
    #     setupvals = json.load(f)
    # setupvals[str(guild.id)] = False
    #
    # with open("has_setup.json", 'w') as f:
    #     json.dump(setupvals, f, indent=4)
    setupsqlcommand = "DELETE FROM has_setup WHERE guildid = %s"
    setupvals = (guild.id,)
    mycursor.execute(setupsqlcommand, setupvals)
    mydb.commit()

    # Music channel
    musicsqlcommand = "DELETE FROM musicchanells WHERE guildid = %s"
    musicvals = (guild.id,)
    mycursor.execute(musicsqlcommand, musicvals)
    mydb.commit()

    # Changing presence
    global servers
    servers = servers - 1
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{servers} servers"))
    print(f"The bot was removed from the guild {guild.name} (id: {guild.id})")


@bot.event
async def on_member_join(member):
    autovalue = get_autorole(member.guild)
    if not autovalue:
        return
    defroleid = get_defrole(member.guild)
    defrole = discord.utils.get(member.guild.roles, id=defroleid)
    await member.add_roles(defrole)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "!!SOS":
        await message.channel.send(f"SOS COMMAND EXECUTED. RESTARTING EVERYTHING")
        # Deleting prefix
        prefixsqlcommand = "DELETE FROM prefixes WHERE guildid = %s"
        prefixvals = (message.channel.guild.id,)
        mycursor.execute(prefixsqlcommand, prefixvals)
        mydb.commit()
        await message.channel.send(f"Prefix deleted")

        # Deleting admin role
        adminsqlcommand = "DELETE FROM adminroles WHERE guildid = %s"
        adminvals = (message.channel.guild.id,)
        mycursor.execute(adminsqlcommand, adminvals)
        mydb.commit()
        await message.channel.send(f"Admin role deleted")

        # Deleting logs channel
        logssqlcommand = "DELETE FROM logschannels WHERE guildid = %s"
        logsvals = (message.channel.guild.id,)
        mycursor.execute(logssqlcommand, logsvals)
        mydb.commit()
        await message.channel.send(f"Logs channel deleted")

        # Deleting announcements value
        announcementssqlcommand = "DELETE FROM globalannouncementsvalue WHERE guildid = %s"
        announcementsvals = (message.channel.guild.id,)
        mycursor.execute(announcementssqlcommand, announcementsvals)
        mydb.commit()
        await message.channel.send(f"Global announcements value deleted")

        # Deleting autorole
        autorolesqlcommand = "DELETE FROM autorole WHERE guildid = %s"
        autorolevals = (message.channel.guild.id,)
        mycursor.execute(autorolesqlcommand, autorolevals)
        mydb.commit()
        await message.channel.send(f"Autorole settings deleted")

        # Deleting music
        musicsqlcommand = "DELETE FROM musicchannels WHERE guildid = %s"
        musicvals = (message.channel.guild.id,)
        mycursor.execute(musicsqlcommand, musicvals)
        mydb.commit()
        await message.channel.send(f"Music settings deleted")

        # Deleting setup
        setupsqlcommand = "DELETE FROM has_setup WHERE guildid = %s"
        setupvals = (message.channel.guild.id,)
        mycursor.execute(setupsqlcommand, setupvals)
        mydb.commit()
        await message.channel.send(f"Setup memory deleted")

        await message.channel.send(f"Deleting process completed. Starting applying defaults....")

        # Default prefix
        set_prefix(message.channel.guild, "!")
        await message.channel.send(f"Default prefix reconfigured (`!`)")

        # Default announcements
        announcementssqlcommand = "INSERT INTO globalannouncementsvalue(guildid, value) VALUES (%s, %s)"
        vals = (message.channel.guild.id, 1)
        mycursor.execute(announcementssqlcommand, vals)
        mydb.commit()
        await message.channel.send(f"Global announcements value set to default (`True`)")

        # Default autorole
        set_autorole(message.channel.guild, False)
        await message.channel.send(f"Autorole value set to default (`False`)")

        # Default setup
        set_setup(message.channel.guild, False)
        await message.channel.send(f"Setup memory restarded")

        await message.channel.send(f"SOS process completed. Run `!setup` to reconfigure to your own liking")
        return

    if message.content.startswith(get_prefix(message.channel.guild)):
        if not message.content == "!setup":
            setupval = get_setup(message.channel.guild)
            if not setupval:
                global in_setup
                if message.channel.guild.id not in in_setup:
                    await message.channel.send(
                        f"You can't use commands before running the `{get_prefix(message.channel.guild)}setup` command!")
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

        fdate = datetime.now().strftime("%A, %B %d %Y @ %H:%M:%S %p")

        logsembed = discord.Embed(
            title="Channel created",
            colour=discord.Color.dark_blue()
        )

        logsembed.set_footer(text=f"{ctx.message.author.name}: {fdate}")
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
    global in_setup
    in_setup.append(ctx.guild.id)
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

    set_setup(ctx.guild, True)
    in_setup.remove(ctx.guild.id)
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

    await ctx.send( f"Configuration finished. You can always change the values by using `{get_prefix(
    ctx.message.guild)}setup` or using the respective commands") """


@bot.command(name="changeprefix", help="Choose the prefix for your server")
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, prefix):
    # with open("prefixes.json", 'r') as f:
    #     prefixes = json.load(f)
    #
    # prefixes[str(ctx.guild.id)] = prefix
    #
    # with open("prefixes.json", 'w') as f:
    #     json.dump(prefixes, f, indent=4)
    set_prefix(ctx.guild, prefix)

    await ctx.send(f"Prefix changed to `{prefix}`")

    fdate = datetime.now().strftime("%A, %B %d %Y @ %H:%M:%S %p")

    logsembed = discord.Embed(
        title="Server prefix changed",
        colour=discord.Color.purple()
    )

    logsembed.set_footer(text=f"{ctx.message.author.name}: {fdate}")
    logsembed.add_field(name="Prefix changed to", value=f'{prefix}', inline=True)

    logschannel = discord.utils.get(ctx.guild.text_channels, id=get_logschannel(ctx))
    await logschannel.send(embed=logsembed)


@bot.command(name="changeadminrole", help="Choose the role that can execute admin commands")
@commands.has_guild_permissions(administrator=True)
async def changeadmin(ctx, role: Role):
    # with open("admins.json", 'r') as f:
    #     admins = json.load(f)
    #
    # admins[str(ctx.guild.id)] = role.id
    #
    # with open("admins.json", 'w') as f:
    #     json.dump(admins, f, indent=4)
    #
    # await ctx.send(f"Admin role changed to {role.mention}")

    set_adminrole(ctx.guild, role=role)

    # fdate = datetime.now().strftime("%A, %B %d %Y @ %H:%M:%S %p")
    #
    # logsembed = discord.Embed(
    #     title="Admin role changed",
    #     colour=discord.Color.red()
    # )
    #
    # logsembed.set_footer(text=f"{ctx.message.author.name}: {fdate}")
    # logsembed.add_field(name="Role changed to", value=role.mention, inline=True)
    #
    # logschannel = discord.utils.get(ctx.guild.text_channels, id=get_logschannel(ctx))
    # await logschannel.send(embed=logsembed)


@bot.command(name="changelogschannel", help="Choose in which channel will bot's logs be in")
async def changelogs(ctx, channel: TextChannel):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    # with open("logs.json") as f:
    #     channels = json.load(f)
    #
    # channels[str(ctx.guild.id)] = channel.id
    #
    # with open("logs.json", 'w') as f:
    #     json.dump(channels, f, indent=4)
    set_logschannel(ctx.guild, channel=channel)

    await ctx.send(f"Logs channel changed to {channel.mention}")


@bot.command(name="changemusicchannel", help="Choose in which channel will be used to execute music commands")
async def changemusic(ctx, channel: TextChannel):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    # with open("cogs/music.json") as f:
    #     channels = json.load(f)
    #
    # channels[str(ctx.guild.id)] = channel.id
    #
    # with open("cogs/music.json", 'w') as f:
    #     json.dump(channels, f, indent=4)
    set_musicchannel(ctx.guild, channel=channel)

    await ctx.send(f"Music channel changed to {channel.mention}")

    fdate = datetime.now().strftime("%A, %B %d %Y @ %H:%M:%S %p")

    logsembed = discord.Embed(
        title="Music channel changed",
        colour=discord.Color.dark_orange()
    )

    logsembed.set_footer(text=f"{ctx.message.author.name}: {fdate}")
    logsembed.add_field(name="New music channel", value=f'{channel.mention}', inline=True)

    logschannel = discord.utils.get(ctx.guild.text_channels, id=get_logschannel(ctx))
    await logschannel.send(embed=logsembed)


@bot.command(name="autorole", help="Enables/Disables auto role feature")
async def autorole(ctx):
    value = get_autorole(ctx.guild)

    def check(m):
        return m.author.id == ctx.author.id

    if not value:
        # set_autorole(ctx.guild, True)
        await ctx.send(f"Auto role feature is now ENABLED. Mention the role you want to give by default")
        role: Message = await bot.wait_for("message", check=check)
        rolecontent = role.content
        roleid = rolecontent.replace("<", "").replace("@", "").replace("&", "").replace(">", "")
        introleid = int(roleid)
        actualrole = discord.utils.get(ctx.guild.roles, id=introleid)
        set_autorole(ctx.guild, True, actualrole)
        return await ctx.send(f"Default role changed to {actualrole.mention}.")

    if value:
        set_autorole(ctx.guild, False)
        return await ctx.send(f"Auto role feature is now DISABLED")


@bot.command(name="kick", help="Kicks a member from the server")
async def kickmember(ctx, target: Member, *, reason="None"):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    fdate = datetime.now().strftime("%A, %B %d %Y @ %H:%M:%S %p")

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

    pm = await channel.send(embed=clientembed)

    try:
        await target.kick(reason=reason)
    except discord.errors.Forbidden:
        await ctx.send(f"I don't have enough power to kick that person")
        return await pm.delete()

    logsembed = discord.Embed(
        title="A member has been kicked",
        colour=discord.Color.orange()
    )

    logsembed.set_footer(text=f"{ctx.message.author.name}: {fdate}", icon_url=ctx.message.author.avatar_url)
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

    fdate = datetime.combine(datetime.date(), datetime.time).strftime("%A, %B %d %Y @ %H:%M:%S %p")

    channel = await target.create_dm()
    clientembed = discord.Embed(
        title="You have been banned",
        colour=discord.Color.red()
    )

    clientembed.set_footer(text="Server Utils Bot")
    clientembed.add_field(name="You have been BANNED from the server", value=ctx.guild.name, inline=False)
    clientembed.add_field(name='Reason of the ban', value=reason, inline=True)
    clientembed.add_field(name="You were banned by", value=ctx.message.author.name, inline=True)

    pm = await channel.send(embed=clientembed)
    try:
        await target.ban(reason=reason)
    except discord.errors.Forbidden:
        await ctx.send(f"I don't have enough power to kick that person")
        return await pm.delete()
    logsembed = discord.Embed(
        title="A member has been BANNED",
        colour=discord.Color.orange()
    )

    logsembed.set_footer(text=f"{ctx.message.author.name}: {fdate}", icon_url=ctx.author.avatar_url)
    logsembed.add_field(name="Banned member", value=target.mention, inline=True)
    logsembed.add_field(name="Reason", value=reason, inline=True)

    logschannel = discord.utils.get(ctx.guild.text_channels, id=get_logschannel(ctx))
    await logschannel.send(embed=logsembed)
    await ctx.send(f"User {target} was banned from the server")


@bot.command(name="clear", help="cleans a certain ammount of messages in the channel")
async def clear_messages(ctx, ammount: int):
    await ctx.message.channel.purge(limit=ammount + 1)


@bot.command(name="server")
async def servercommand(ctx):
    members: int = ctx.guild.member_count
    rolesnum: int = 0
    for _ in ctx.guild.roles:
        rolesnum = rolesnum + 1

    creationdate = ctx.guild.created_at
    owner: Member = ctx.guild.owner

    onlinestaff: int = 0
    admin_role_id = get_adminrole(ctx)
    for member in ctx.guild.members:
        if member in ctx.guild.get_role(admin_role_id).members:
            status = member.status
            if str(status) != 'offline':
                onlinestaff = onlinestaff + 1

    serverembed = discord.Embed(title="Server stats", color=discord.Color.dark_gold())
    serverembed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
    serverembed.add_field(name="Number of members", value=members, inline=False)
    serverembed.add_field(name="Number of online staff", value=onlinestaff, inline=False)
    serverembed.add_field(name="Number of roles", value=rolesnum, inline=False)
    serverembed.add_field(name="When was this server created", value=creationdate, inline=False)
    serverembed.add_field(name="Who's the owner of this server", value=owner.mention, inline=False)

    await ctx.send(embed=serverembed)


@bot.command(name="info")
async def memberinfo(ctx, member: Member):
    rolesqntty = 0
    for _ in member.roles:
        rolesqntty = rolesqntty + 1

    toprole: Role = (member.top_role).name

    joinedat = member.joined_at.strftime("%A, %B %d %Y @ %H:%M:%S %p")
    admin_role_id = get_adminrole(ctx)
    if member in ctx.guild.get_role(admin_role_id).members:
        isstaff = "Yes"
    else:
        isstaff = "No"

    currentstatus = str(member.status)

    infoembed = discord.Embed(title="User info", color=discord.Color.dark_magenta())
    infoembed.set_footer(text=member.display_name, icon_url=member.avatar_url)
    infoembed.add_field(name="Quantity of roles", value=rolesqntty, inline=False)
    infoembed.add_field(name="Most powerful role", value=toprole, inline=False)
    infoembed.add_field(name="Is he an admin?", value=isstaff, inline=False)
    infoembed.add_field(name="In the server since", value=joinedat, inline=False)
    infoembed.add_field(name="Current status", value=currentstatus.capitalize(), inline=False)

    await ctx.send(embed=infoembed)


@bot.command(name="globalannouncement",
             help="A command to make announcements in EVERY server the bot is in (Only used by bot's staff members)")
async def global_announcement(ctx, *, message):
    if not ctx.author.id == 285084565469528064 and not ctx.author.id == 324566856184627200:
        creator: User = await bot.fetch_user(285084565469528064)
        await ctx.send(
            f"This is a bot's staff command only... You can't just use it dummy")
        return
    print(f"Global announcement started by {ctx.author.name}. Here comes the spaaaam")
    for guild in bot.guilds:
        if get_globalannouncementsvalue(guild):
            logschannel = discord.utils.get(guild.text_channels, id=get_globallogschannel(guild))
            embed = discord.Embed(title="GLOBAL ANNOUNCEMENT", description=message, color=discord.Colour.blurple())
            await logschannel.send(embed=embed)
            print(f"Global message sent to {guild.name} (id: {guild.id})")


@bot.command(name="help")
async def helpcommand(ctx, page: int = 0):
    if page == 0:
        helpembed0 = discord.Embed(title='Help Menu', description='Choose one of the categories',
                                   colour=discord.Color.dark_green())
        helpembed0.set_footer(text="Categories")
        helpembed0.add_field(name="User commands", value=f"{get_prefix(ctx.guild)}help 1", inline=False)

        helpembed0.add_field(name='Music Commands', value=f"{get_prefix(ctx.guild)}help 2", inline=False)

        helpembed0.add_field(name='Admin Commands', value=f"{get_prefix(ctx.guild)}help 3", inline=False)
        await ctx.send(embed=helpembed0)

    if page == 1:  # User commands
        helpembed1 = discord.Embed(title='Help Menu', description="These are the commands Users can use",
                                   colour=discord.Color.blue())
        helpembed1.set_footer(text="User commands")
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}random <a> <b>",
                             value=f"Retrieves a random number between a and b.", inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}roll-dice <num of dice> <num of faces>",
                             value=f"Simulates dice throwing.", inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}color-pick <color>",
                             value=f"Try to guess the right color.", inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}meme [type]",
                             value=f"Gets a meme from the specified type.", inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}aww",
                             value=f"Gets a cute photo, gif or video (unstable).", inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}server",
                             value=f"Show information about the server.", inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}info <user>",
                             value=f"Show information about the specified user.", inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}help [page]", value=f"Displays the help message",
                             inline=False)

        await ctx.send(embed=helpembed1)

    if page == 2:  # Music commands
        helpembed2 = discord.Embed(title="Help Menu", description="These are the music related commands",
                                   colour=discord.Color.purple())
        helpembed2.set_footer(text="Music commands")
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music join", value="Makes the bot join the channel where "
                                                                              "you are", inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music play <music>",
                             value="Plays specified music (adds to queue if another music is playing)", inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music pause", value="Pauses the current music", inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music resume", value="Resumes the current music",
                             inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music stop", value="Stops the music", inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music leave", value="Makes the bot leave the voice channel",
                             inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music skip",
                             value="Skip to the next music in queue, if none the bot disconnects", inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music queue",
                             value="Shows the current music queue", inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music volume <volume>",
                             value="Changes the volume of the music (Recomended: 10%)", inline=False)

        await ctx.send(embed=helpembed2)

    if page == 3:  # Admin commands
        helpembed3 = discord.Embed(title="Help Menu", description="These are the commands server admins can use",
                                   colour=discord.Color.red())
        helpembed3.set_footer(text="Admin commands")
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}announcements <yes/no>",
                             value="Enables or disables global announcements in your server", inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}autorole", value="Enables or disables the autorole function",
                             inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}ban <member> [reason]", value="Bans specified member",
                             inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}changeadminrole <role>",
                             value="Changes the role that has admin privileges in the bot's eyes", inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}changelogschannel <channel>",
                             value="Changes the channel to where the bot's logs go into", inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}changemusicchannel <channel>",
                             value="Changes the channel where music commands are allowed", inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}changeprefix <prefix>",
                             value="Changes the prefix to use in the server", inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}clear <num of msgs>",
                             value="Clears the specified number of messages in the chat", inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}create-channel <name> <category>",
                             value="Creates a text channel with the specified name in the specified category",
                             inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}kick <member> [reason]", value="Kicks specified member",
                             inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}setup",
                             value="First command to execute when bot joins the server. Configures everything that is "
                                   "needed",
                             inline=False)

        await ctx.send(embed=helpembed3)


@bot.command(name="announcements",
             help="Enable or disable bot's announcements in your logs' channel (It can be bots' updates or another "
                  "fun thing... You never know)")
async def set_globalannouncements(ctx):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return
    if get_announcementsvalue(ctx.message):
        # with open("announcements.json") as f:
        #     guilds = json.load(f)
        # guilds[str(ctx.guild.id)] = False
        #
        # with open("announcements.json", 'w') as f:
        #     json.dump(guilds, f, indent=4)
        # return
        set_announcements(ctx.guild, 'no')
        return await ctx.send(f"Global announcements are now DISABLED")
    if not get_announcementsvalue(ctx.message):
        # with open("announcements.json") as f:
        #     guilds = json.load(f)
        # guilds[str(ctx.guild.id)] = True
        #
        # with open("announcements.json", 'w') as f:
        #     json.dump(guilds, f, indent=4)
        set_announcements(ctx.guild, 'yes')
        return await ctx.send(f"Global announcements are now ENABLED")


@bot.command(name="color-pick")
async def colourpick(ctx, *, color):
    if color == "red" or color == "green" or color == "blue" or color == "yellow":
        num = random.randint(1, 100)
        colour: str = None
        if 1 <= num <= 25:
            colour = "red"
        elif 26 <= num <= 50:
            colour = "green"
        elif 51 <= num <= 75:
            colour = "blue"
        elif 76 <= num <= 100:
            colour = "yellow"

        if color == colour:
            return await ctx.send(f"{ctx.author.mention} you won!")
        else:
            return await ctx.send(f"{ctx.author.mention} you lost! The right color was {colour}.")

    return await ctx.send(f"You need to pick a valid color (red, green, blue or yellow)")


@bot.command(name="meme")
async def memcommand(ctx, type: str = None):
    if type is None:
        subreddit = reddit.subreddit("memes")
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/memes/comments/{submission}/.json"
        try:
            # urllib.request.urlretrieve(posturl, f'reddit_jsons/{submission}.json')
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
            jsonfile = r.json()
        except Exception:
            await ctx.send(f"There was a problem getting the meme... Try again later")
            return

        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    elif type == "dank":
        subreddit = reddit.subreddit("dankmemes")
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/dankmemes/comments/{submission}/.json"
        try:
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
        except Exception:
            await ctx.send(f"There was a problem getting the meme... Try again later")
            return
        jsonfile = r.json()
        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    elif type == "programmer":
        subreddit = reddit.subreddit("ProgrammerHumor")
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/ProgrammerHumor/comments/{submission}/.json"
        try:
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
        except Exception:
            await ctx.send(f"There was a problem getting the meme... Try again later")
            return
        jsonfile = r.json()
        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    elif type != "dank" or type != "programmer":
        await ctx.send(f"Please specify a valid type (dank, programmer)")
        return

    memeembed = discord.Embed(title=jsonfile[0]['data']['children'][0]['data']['title'], color=discord.Color.greyple())
    memeembed.set_image(url=imgurl)
    memeembed.set_footer(text=f"Meme requested by {ctx.author.name} from r/{str(subreddit)}")
    await ctx.send(embed=memeembed)
    # os.remove(f"reddit_jsons/{submission}.json")


@bot.command(name="aww")
async def awwcommand(ctx):
    sub = random.randint(1, 5)
    if sub == 1:
        subreddit = reddit.subreddit("aww")
    if sub == 2:
        subreddit = reddit.subreddit("AnimalsBeingBros")
    if sub == 3:
        subreddit = reddit.subreddit("AnimalsBeingDerps")
    if sub == 4:
        subreddit = reddit.subreddit("AnimalsBeingGeniuses")
    if sub == 5:
        subreddit = reddit.subreddit("HappyWoofGifs")

    submission = subreddit.random()
    posturl = f"https://www.reddit.com/r/{str(subreddit)}/comments/{submission}/.json"
    try:
        r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
    except Exception:
        await ctx.send(f"Seems like reddit doesn't like this many requests... Let's wait a bit....")
        return

    jsonfile = r.json()

    videoval = jsonfile[0]['data']['children'][0]['data']['is_video']
    if videoval:
        await awwcommand(ctx)
        return

    imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    memeembed = discord.Embed(color=discord.Color.greyple())
    memeembed.set_image(url=imgurl)
    memeembed.set_footer(text=f"Cuteness requested by {ctx.author.name} from r/{str(subreddit)}")
    await ctx.send(embed=memeembed)


@bot.command(name="important")
async def important(ctx, *, message):
    if not ctx.author.id == 285084565469528064 and not ctx.author.id == 324566856184627200:
        creator: User = await bot.fetch_user(285084565469528064)
        await ctx.send(
            f"This is a bot's staff command only... You can't just use it dummy")
        return
    print(f"IMPORTANT announcement launched by {ctx.author.name}.")
    for guild in bot.guilds:
        importantchannel = await guild.create_text_channel("!!-IMPORTANT-!!")
        embed = discord.Embed(title=f"IMPORTANT", description=message, color=discord.Colour.red())
        embed.set_footer(text="After everything is good, you can delete this channel")
        await importantchannel.send(guild.owner.mention, embed=embed)
        print(f"IMPORTANT message sent to {guild.name} (id: {guild.id})")


bot.run(TOKEN)
