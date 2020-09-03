# sys.path.insert(1, 'cogs/')
import asyncio
import atexit
import os
import random
from datetime import datetime

import discord
import emoji
import mysql.connector as mysql
import requests
from discord import CategoryChannel
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
invites = {}
mydb = None
mycursor = None


# Connect to mysql
def connectmysql():
    global mydb
    global mycursor
    while True:
        try:
            mydb = mysql.connect(
                # host="[HOST]",
                # user="[USER]",
                # password="[PASS]",
                # database="[DB]"
                host="[HOST]",
                user="[USER]",
                password="[PASS]",
                database="[DB]"
            )
            print(f"Bot Connected to database")
            break
        except mysql.Error as error:
            print(f"Couldn't establish connection to mysql server. Reason: {error}")
            continue

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
        if mydb is not None:
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


def get_logschannel_by_guild(guild: Guild):
    sqlcommand = "SELECT channelid FROM logschannels WHERE guildid = %s"
    vals = (guild.id,)
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
    try:
        sqlcommand = "SELECT channelid FROM logschannels WHERE guildid = %s"
        vals = (guild.id,)
        mycursor.execute(sqlcommand, vals)
        result = mycursor.fetchall()
        strchannelid = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
        channelid = int(strchannelid)
        return channelid
    except:
        return None


def get_pornvalue(guild: Guild):
    sqlcommand = "SELECT value FROM porn WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strresult = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    intresult = int(strresult)
    boolresult = bool(intresult)
    return boolresult


def get_user_invites(guild: Guild, member: Member):
    sqlcommand = "SELECT quantity FROM user_invites WHERE guildid = %s AND userid = %s"
    vals = (guild.id, member.id)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    if not result:
        return 0
    return int(result[0][0])


def get_used_invite_code(guild: Guild, invited: Member):
    sqlcommand = "SELECT code FROM used_invite WHERE guildid = %s AND userid = %s"
    vals = (guild.id, invited.id)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    return str(result[0][0])


def exiting():
    if mydb is not None:
        mycursor.close()
        print(f"Disconnected from database")


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


def get_joinvalue(guild: Guild):
    sqlcommand = "SELECT join_value FROM join_leave_messages WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strresult = str(result[0][0])
    intresult = int(strresult)
    boolresult = bool(intresult)
    return boolresult


def get_joinmessage(guild: Guild):
    sqlcommand = "SELECT join_channelid, join_message FROM join_leave_messages WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    return [int(result[0][0]), str(result[0][1])]


def get_leavevalue(guild: Guild):
    sqlcommand = "SELECT leave_value FROM join_leave_messages WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strresult = str(result[0][0])
    intresult = int(strresult)
    boolresult = bool(intresult)
    return boolresult


def get_leavemessage(guild: Guild):
    sqlcommand = "SELECT leave_channelid, leave_message FROM join_leave_messages WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    return [int(result[0][0]), str(result[0][1])]


def get_ticket(guild: Guild):
    sqlcommand = "SELECT value FROM ticketsystem WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strresult = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    intresult = int(strresult)
    boolresult = bool(intresult)
    return boolresult


def get_ticketchannels(guild: Guild):
    sqlcommand = "SELECT channelid, categoryid FROM ticketsystem WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    channels = dict()
    split = str(result[0]).split(", ")
    channelid = int(str(split[0]).replace("(", ""))
    categoryid = int(str(split[1]).replace(")", ""))
    channels["channelid"] = channelid
    channels["categoryid"] = categoryid
    return channels


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
def set_prefix(guild: Guild, prefix: str):
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


def set_join_message(guild: Guild, value: bool, channel: TextChannel = None, message: str = None):
    checksqlcommand = "SELECT * FROM join_leave_messages WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if not result:
        if value:
            sqlcommand = "INSERT INTO join_leave_messages(guildid, join_value, join_channelid, join_message) VALUES (%s, %s, %s, %s)"
            vals = (guild.id, 1, channel.id, message)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
        if not value:
            sqlcommand = "INSERT INTO join_leave_messages(guildid, join_value) VALUES (%s, %s)"
            vals = (guild.id, 0)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
    if result:
        if value:
            sqlcommand = "UPDATE join_leave_messages SET join_value = %s, join_channelid = %s, join_message = %s WHERE guildid = %s"
            vals = (1, channel.id, message, guild.id)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
        if not value:
            sqlcommand = "UPDATE join_leave_messages SET join_value = %s WHERE guildid = %s"
            vals = (0, guild.id)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()


def set_leave_message(guild: Guild, value: bool, channel: TextChannel = None, message: str = None):
    checksqlcommand = "SELECT * FROM join_leave_messages WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if not result:
        if value:
            sqlcommand = "INSERT INTO join_leave_messages(guildid, leave_value, leave_channelid, leave_message) VALUES (%s, %s, %s, %s)"
            vals = (guild.id, 1, channel.id, message)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
        if not value:
            sqlcommand = "INSERT INTO join_leave_messages(guildid, leave_value) VALUES (%s, %s)"
            vals = (guild.id, 0)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
    if result:
        if value:
            sqlcommand = "UPDATE join_leave_messages SET leave_value = %s, leave_channelid = %s, leave_message = %s WHERE guildid = %s"
            vals = (1, channel.id, message, guild.id)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
        if not value:
            sqlcommand = "UPDATE join_leave_messages SET leave_value = %s WHERE guildid = %s"
            vals = (0, guild.id)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()


def get_inviteleaderboard(guild: Guild):
    sqlcommand = "SELECT userid, quantity FROM user_invites WHERE guildid = %s ORDER BY quantity DESC"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    return result


def set_ticketsystem(guild: Guild, value: bool, channel: TextChannel = None, category: CategoryChannel = None):
    checksqlcommand = "SELECT * FROM ticketsystem WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if result:
        if value:
            sqlcommand = "UPDATE ticketsystem SET value = %s, channelid = %s, categoryid = %s WHERE guildid = %s"
            vals = (1, channel.id, category.id, guild.id)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
        if not value:
            sqlcommand = "UPDATE ticketsystem SET value = %s WHERE guildid = %s"
            vals = (0, guild.id)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
    if not result:
        if value:
            sqlcommand = "INSERT INTO ticketsystem(guildid, value, channelid, categoryid) VALUES (%s, %s, %s, %s)"
            vals = (guild.id, 1, channel.id, category.id)
            mycursor.execute(sqlcommand, vals)
            mydb.commit()
        if not value:
            sqlcommand = "INSERT INTO ticketsystem(guildid, value) VALUES (%s, %s)"
            vals = (guild.id, 0)


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


def set_porn(guild: Guild, value: bool):
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

    checksqlcommand = "SELECT * FROM porn WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if result:
        sqlcommand = "UPDATE porn SET value = %s WHERE guildid = %s"
        vals = (value, guild.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
    if not result:
        sqlcommand = "INSERT INTO porn(guildid, value) VALUES (%s, %s)"
        vals = (guild.id, value)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()


def set_user_invites(guild: Guild, member: Member, ammount: int):
    checksqlcommand = "SELECT quantity FROM user_invites WHERE guildid = %s AND userid = %s"
    checkvals = (guild.id, member.id)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if not result:
        sqlcommand = "INSERT INTO user_invites(guildid, userid, quantity) VALUES (%s, %s, %s)"
        vals = (guild.id, member.id, ammount)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
    if result:
        if ammount < 0:
            ammount = 0
        sqlcommand = "UPDATE user_invites SET quantity = %s WHERE guildid = %s AND userid = %s"
        vals = (ammount, guild.id, member.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()


def set_used_invite(guild: Guild, invited: Member, code: str):
    checksqlcommand = "SELECT * FROM used_invite WHERE guildid = %s AND userid = %s"
    checkvals = (guild.id, invited.id)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()
    if not result:
        sqlcommand = "INSERT INTO used_invite(guildid, userid, code) VALUES (%s, %s, %s)"
        vals = (guild.id, invited.id, code)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
    if result:
        sqlcommand = "UPDATE used_invite SET code = %s WHERE guildid = %s AND userid = %s"
        vals = (code, guild.id, invited.id)
        mydb.commit()


def find_invite_by_code(invite_list, code):
    for inv in invite_list:
        if inv.code == code:
            return inv


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
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"{servers} servers | !help"))
    bot.load_extension('cogs.music')
    keep_mysql.start()
    await asyncio.sleep(4)
    for guild in bot.guilds:
        #     checkporncommand = "SELECT * FROM porn where guildid = %s"
        #     vals = (guild.id,)
        #     mycursor.execute(checkporncommand, vals)
        #     result = mycursor.fetchall()
        #     if not result:
        #         set_porn(guild, False)
        checkjoinleave = "SELECT * FROM join_leave_messages WHERE guildid = %s"
        checkjoinleavevals = (guild.id,)
        mycursor.execute(checkjoinleave, checkjoinleavevals)
        joinleaveresult = mycursor.fetchall()
        if not joinleaveresult:
            set_join_message(guild, False)
            set_leave_message(guild, False)

    for guild in bot.guilds:
        invites[guild.id] = await guild.invites()

    print(f"Bot successfully initiated")

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

    # Porn value
    set_porn(guild, False)

    # Invite messages
    set_join_message(guild, False)
    set_leave_message(guild, False)

    # Messaging server owner
    embed = discord.Embed(title="Hey, looks like I'm in your server!",
                          description="You're receiving this message because I entered your discord server. I know we "
                                      "will have a ball together!",
                          colour=discord.Colour.green(),
                          inline=False)
    embed.add_field(name="Setup command",
                    value="The setup command is the best way to start our journey. Hop in a private channel in your "
                          "discord server and use it!")
    embed.add_field(name="Discord support server",
                    value="I have a support server. If you have any issues or suggestions hop in there and write freely. We await you!\nLink:https://discord.gg/gWmhSRD",
                    inline=False)
    # embed.add_field(name="Link", value="https://github.com/xlysander12/Server-Utils", inline=True)

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
    musicsqlcommand = "DELETE FROM musicchannels WHERE guildid = %s"
    musicvals = (guild.id,)
    mycursor.execute(musicsqlcommand, musicvals)
    mydb.commit()

    # Porn value
    pornsqlcommand = "DELETE FROM porn WHERE guildid = %s"
    pornvals = (guild.id,)
    mycursor.execute(pornsqlcommand, pornvals)
    mydb.commit()

    # Invite Messages
    invitessqlcommand = "DELETE FROM join_leave_messages WHERE guildid = %s"
    invitesvals = (guild.id,)
    mycursor.execute(invitessqlcommand, invitesvals)
    mydb.commit()

    # Changing presence
    global servers
    servers = servers - 1
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{servers} servers"))
    print(f"The bot was removed from the guild {guild.name} (id: {guild.id})")


@bot.event
async def on_member_join(member: Member):
    autovalue = get_autorole(member.guild)
    if autovalue:
        defroleid = get_defrole(member.guild)
        defrole = discord.utils.get(member.guild.roles, id=defroleid)
        await member.add_roles(defrole)

    invites_before_join = invites[member.guild.id]
    invites_after_join = await member.guild.invites()
    used_invite: discord.Invite = None
    for invite in invites_before_join:
        if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
            # print(f"Member {member.name} Joined")
            # print(f"Invite code: {invite.code}")
            # print(f"Inviter {invite.inviter}")
            set_user_invites(member.guild, invite.inviter, get_user_invites(member.guild, invite.inviter) + 1)
            set_used_invite(member.guild, member, invite.code)
            used_invite = invite
            invites[member.guild.id] = invites_after_join
            break
    # await discord.utils.get(member.guild.text_channels, id=get_logschannel_by_guild(member.guild)).send(f"{member.mention} just joined the server (invited by: {invite.inviter.mention})")
    if get_joinvalue(member.guild):
        join_channelmessage = get_joinmessage(member.guild)
        channelid = join_channelmessage[0]
        message = emoji.emojize(join_channelmessage[1])
        actualchannel: TextChannel = discord.utils.get(member.guild.text_channels, id=channelid)
        # print(member.guild.name)
        # print(member.display_name)
        # print(member.mention)
        # print(used_invite.inviter.display_name)
        # print(used_invite.inviter.mention)
        # print(used_invite.code)
        # print(f"https://discord.gg/{used_invite.code}")
        # print(get_user_invites(member.guild, used_invite.inviter))
        variabled_message: str = message.replace("$server_name", member.guild.name).replace("$user_name",
                                                                                            member.display_name).replace(
            "$user_mention", member.mention).replace("$inviter_name", used_invite.inviter.name).replace(
            "$inviter_mention", used_invite.inviter.mention).replace("$invite_code", used_invite.code).replace(
            "$invite_link", f"https://discord.gg/{used_invite.code}").replace("$invites_number", str(
            get_user_invites(member.guild, used_invite.inviter)))
        embed = discord.Embed(description=variabled_message, color=discord.Color.green())
        await actualchannel.send(embed=embed)


@bot.event
async def on_member_remove(member: Member):
    used_invite: discord.Invite = await bot.fetch_invite(f"discord.gg/{get_used_invite_code(member.guild, member)}")
    set_user_invites(member.guild, used_invite.inviter, get_user_invites(member.guild, used_invite.inviter) - 1)
    invites[member.guild.id] = await member.guild.invites()
    if get_leavevalue(member.guild):
        leave_channelmessage = get_leavemessage(member.guild)
        channelid = leave_channelmessage[0]
        message = emoji.emojize(leave_channelmessage[1])
        actualchannel = discord.utils.get(member.guild.text_channels, id=channelid)
        variabled_message: str = message.replace("$server_name", member.guild.name).replace("$user_name",
                                                                                            member.display_name).replace(
            "$user_mention", member.mention).replace("$inviter_name", used_invite.inviter.name).replace(
            "$inviter_mention", used_invite.inviter.mention).replace("$invite_code", used_invite.code).replace(
            "$invite_link", f"https://discord.gg/{used_invite.code}").replace("$invites_number", str(
            get_user_invites(member.guild, used_invite.inviter)))
        embed = discord.Embed(description=variabled_message, color=discord.Colour.red())
        await actualchannel.send(embed=embed)


@bot.event
async def on_invite_create(invite: discord.Invite):
    invites[invite.guild.id] = await invite.guild.invites()


@bot.event
async def on_invite_delete(invite: discord.Invite):
    invites[invite.guild.id] = await invite.guild.invites()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "!!SOS":
        if not message.author.guild_permissions.administrator:
            return await message.channel.send(f"You are not an administrator")
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

        # Default autorole
        set_autorole(message.channel.guild, False)
        await message.channel.send(f"+18 content value set to default (`False`)")

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
    # msg: Message = await ctx.send(f"Lets start the setup... First write what you want the prefix for your server to be")
    setupembed1 = discord.Embed(title=f"Setup Configuration",
                                description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                color=discord.Color.purple())
    setupembed1.add_field(name=f"New prefix", value=f"---", inline=False)
    setupembed1.add_field(name=f"Admin role", value=f"---", inline=False)
    setupembed1.add_field(name=f"Logs channel", value=f"---", inline=False)
    setupembed1.add_field(name=f"Music channel", value=f"---", inline=False)
    setupembed1.add_field(name=f"Bot's announcements", value=f"---", inline=False)
    setupembed1.add_field(name=f"NSFW content", value=f"---", inline=False)
    setupembed1.add_field(name=f"Autorole", value=f"---", inline=False)
    setupembed1.add_field(name=f"Default role", value=f"---", inline=False)
    setupembed1.add_field(name=f"Ticket system", value=f"---", inline=False)
    setupembed1.add_field(name=f"Ticket channel", value=f"---", inline=False)
    setupembed1.add_field(name=f"Ticket category", value=f"---", inline=False)
    setupembed1.set_footer(text=f"Write the prefix you want to use (default: !)")
    setupembed1.set_thumbnail(url=bot.user.avatar_url)
    setupmsg: Message = await ctx.send(embed=setupembed1)

    def check(m):
        return m.author.id == ctx.author.id

    prefix: Message = await bot.wait_for("message", check=check)
    actualprefix = prefix.content
    await prefix.delete()
    # await ctx.send(f"Prefix changed to {prefix.content}... Let's keep going")

    setupembed2 = discord.Embed(title=f"Setup Configuration",
                                description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                color=discord.Color.purple())
    setupembed2.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
    setupembed2.add_field(name=f"Admin role", value=f"---", inline=False)
    setupembed2.add_field(name=f"Logs channel", value=f"---", inline=False)
    setupembed2.add_field(name=f"Music channel", value=f"---", inline=False)
    setupembed2.add_field(name=f"Bot's announcements", value=f"---", inline=False)
    setupembed2.add_field(name=f"NSFW content", value=f"---", inline=False)
    setupembed2.add_field(name=f"Autorole", value=f"---", inline=False)
    setupembed2.add_field(name=f"Default role", value=f"---", inline=False)
    setupembed2.add_field(name=f"Ticket system", value=f"---", inline=False)
    setupembed2.add_field(name=f"Ticket channel", value=f"---", inline=False)
    setupembed2.add_field(name=f"Ticket category", value=f"---", inline=False)
    setupembed2.set_footer(text=f"Mention the role you want to be able to use admin commands")
    setupembed2.set_thumbnail(url=bot.user.avatar_url)
    await setupmsg.edit(embed=setupembed2)

    # await ctx.send(f"Now, mention the role you want it to be the admin role")
    role: Message = await bot.wait_for("message", check=check)
    rolecontent = role.content
    roleid = rolecontent.replace("<", "").replace("@", "").replace("&", "").replace(">", "")
    introleid = int(roleid)
    actualrole: Role = discord.utils.get(ctx.guild.roles, id=introleid)
    await role.delete()
    # set_adminrole(ctx.message.guild, role=actualrole)
    # await ctx.send(f"Admin role changed to {actualrole.mention}... Let's keep going")

    setupembed3 = discord.Embed(title=f"Setup Configuration",
                                description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                color=discord.Color.purple())
    setupembed3.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
    setupembed3.add_field(name=f"Admin role", value=f"{actualrole.mention}", inline=False)
    setupembed3.add_field(name=f"Logs channel", value=f"---", inline=False)
    setupembed3.add_field(name=f"Music channel", value=f"---", inline=False)
    setupembed3.add_field(name=f"Bot's announcements", value=f"---", inline=False)
    setupembed3.add_field(name=f"NSFW content", value=f"---", inline=False)
    setupembed3.add_field(name=f"Autorole", value=f"---", inline=False)
    setupembed3.add_field(name=f"Default role", value=f"---", inline=False)
    setupembed3.add_field(name=f"Ticket system", value=f"---", inline=False)
    setupembed3.add_field(name=f"Ticket channel", value=f"---", inline=False)
    setupembed3.add_field(name=f"Ticket category", value=f"---", inline=False)
    setupembed3.set_footer(text=f"Mention the channel you want to get the logs")
    setupembed3.set_thumbnail(url=bot.user.avatar_url)
    await setupmsg.edit(embed=setupembed3)

    # await ctx.send(f"Now, mention the channel you want to the logs to go to")
    logsc: Message = await bot.wait_for("message", check=check)
    logsc_content = logsc.content
    logs_id = logsc_content.replace("<", "").replace("#", "").replace("#", "").replace(">", "")

    actual_logsc: TextChannel = discord.utils.get(ctx.guild.text_channels, id=int(logs_id))
    await logsc.delete()
    # set_logschannel(ctx.message.guild, channel=actual_logsc)
    # await ctx.send(f"Logs channel changed to {actual_logsc.mention}... Let's keep going")

    setupembed4 = discord.Embed(title=f"Setup Configuration",
                                description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                color=discord.Color.purple())
    setupembed4.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
    setupembed4.add_field(name=f"Admin role", value=f"{actualrole.mention}", inline=False)
    setupembed4.add_field(name=f"Logs channel", value=f"{actual_logsc.mention}", inline=False)
    setupembed4.add_field(name=f"Music channel", value=f"---", inline=False)
    setupembed4.add_field(name=f"Bot's announcements", value=f"---", inline=False)
    setupembed4.add_field(name=f"NSFW content", value=f"---", inline=False)
    setupembed4.add_field(name=f"Autorole", value=f"---", inline=False)
    setupembed4.add_field(name=f"Default role", value=f"---", inline=False)
    setupembed4.add_field(name=f"Ticket system", value=f"---", inline=False)
    setupembed4.add_field(name=f"Ticket channel", value=f"---", inline=False)
    setupembed4.add_field(name=f"Ticket category", value=f"---", inline=False)
    setupembed4.set_footer(text=f"Mention the channel you want to be used for music commands")
    setupembed4.set_thumbnail(url=bot.user.avatar_url)
    await setupmsg.edit(embed=setupembed4)

    # await ctx.send(f"Now, mention the channel you want to be used for music commands")
    musicc: Message = await bot.wait_for("message", check=check)
    musicc_content = musicc.content
    musicc_id = musicc_content.replace("<", "").replace("#", "").replace("#", "").replace(">", "")

    actual_musicc: TextChannel = discord.utils.get(ctx.guild.text_channels, id=int(musicc_id))
    await musicc.delete()
    # set_musicchannel(ctx.message.guild, channel=actual_musicc)
    # await ctx.send(f"Music channel changed to {actual_musicc.mention}... Let's keep going")

    setupembed5 = discord.Embed(title=f"Setup Configuration",
                                description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                color=discord.Color.purple())
    setupembed5.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
    setupembed5.add_field(name=f"Admin role", value=f"{actualrole.mention}", inline=False)
    setupembed5.add_field(name=f"Logs channel", value=f"{actual_logsc.mention}", inline=False)
    setupembed5.add_field(name=f"Music channel", value=f"{actual_musicc.mention}", inline=False)
    setupembed5.add_field(name=f"Bot's announcements", value=f"---", inline=False)
    setupembed5.add_field(name=f"NSFW content", value=f"---", inline=False)
    setupembed5.add_field(name=f"Autorole", value=f"---", inline=False)
    setupembed5.add_field(name=f"Default role", value=f"---", inline=False)
    setupembed5.add_field(name=f"Ticket system", value=f"---", inline=False)
    setupembed5.add_field(name=f"Ticket channel", value=f"---", inline=False)
    setupembed5.add_field(name=f"Ticket category", value=f"---", inline=False)
    setupembed5.set_footer(text=f"Do you want to receive bot's announcements (yes / no)")
    setupembed5.set_thumbnail(url=bot.user.avatar_url)
    await setupmsg.edit(embed=setupembed5)

    # await ctx.send(f"Do you want to receive announcements about this bot's updates or other stuff? (yes / no)")
    announcements: Message = await bot.wait_for("message", check=check)
    announcements_content = announcements.content
    await announcements.delete()
    # set_announcements(ctx.message.guild, announcements)
    if announcements_content == 'yes':
        functionannouncements = "Enabled"

    if announcements_content == 'no':
        # await ctx.send(f"Global announcements are now disabled")
        functionannouncements = "Disabled"

    setupembed6 = discord.Embed(title=f"Setup Configuration",
                                description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                color=discord.Color.purple())
    setupembed6.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
    setupembed6.add_field(name=f"Admin role", value=f"{actualrole.mention}", inline=False)
    setupembed6.add_field(name=f"Logs channel", value=f"{actual_logsc.mention}", inline=False)
    setupembed6.add_field(name=f"Music channel", value=f"{actual_musicc.mention}", inline=False)
    setupembed6.add_field(name=f"Bot's announcements", value=f"{functionannouncements}", inline=False)
    setupembed6.add_field(name=f"NSFW content", value=f"---", inline=False)
    setupembed6.add_field(name=f"Autorole", value=f"---", inline=False)
    setupembed6.add_field(name=f"Default role", value=f"---", inline=False)
    setupembed6.add_field(name=f"Ticket system", value=f"---", inline=False)
    setupembed6.add_field(name=f"Ticket channel", value=f"---", inline=False)
    setupembed6.add_field(name=f"Ticket category", value=f"---", inline=False)
    setupembed6.set_footer(text=f"Do you want to enable NSFW stuff? (yes / no)")
    setupembed6.set_thumbnail(url=bot.user.avatar_url)
    await setupmsg.edit(embed=setupembed6)

    nsfw: Message = await bot.wait_for("message", check=check)
    nsfw_content = nsfw.content
    await nsfw.delete()
    if nsfw_content == "yes":
        functionnsfw = "Enabled"
    if nsfw_content == "no":
        functionnsfw = "Disabled"

    setupembed7 = discord.Embed(title=f"Setup Configuration",
                                description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                color=discord.Color.purple())
    setupembed7.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
    setupembed7.add_field(name=f"Admin role", value=f"{actualrole.mention}", inline=False)
    setupembed7.add_field(name=f"Logs channel", value=f"{actual_logsc.mention}", inline=False)
    setupembed7.add_field(name=f"Music channel", value=f"{actual_musicc.mention}", inline=False)
    setupembed7.add_field(name=f"Bot's announcements", value=f"{functionannouncements}", inline=False)
    setupembed7.add_field(name=f"NSFW content", value=f"{functionnsfw}", inline=False)
    setupembed7.add_field(name=f"Autorole", value=f"---", inline=False)
    setupembed7.add_field(name=f"Default role", value=f"---", inline=False)
    setupembed7.add_field(name=f"Ticket system", value=f"---", inline=False)
    setupembed7.add_field(name=f"Ticket channel", value=f"---", inline=False)
    setupembed7.add_field(name=f"Ticket category", value=f"---", inline=False)
    setupembed7.set_footer(text=f"Activate autorole feature? (yes / no)")
    setupembed7.set_thumbnail(url=bot.user.avatar_url)
    await setupmsg.edit(embed=setupembed7)

    autrole: Message = await bot.wait_for("message", check=check)
    autrole_content = autrole.content
    await autrole.delete()
    if autrole_content == "yes":
        functionautrole = "Enabled"
        setupembed71 = discord.Embed(title=f"Setup Configuration",
                                     description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                     color=discord.Color.purple())
        setupembed71.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
        setupembed71.add_field(name=f"Admin role", value=f"{actualrole.mention}", inline=False)
        setupembed71.add_field(name=f"Logs channel", value=f"{actual_logsc.mention}", inline=False)
        setupembed71.add_field(name=f"Music channel", value=f"{actual_musicc.mention}", inline=False)
        setupembed71.add_field(name=f"Bot's announcements", value=f"{functionannouncements}", inline=False)
        setupembed71.add_field(name=f"NSFW content", value=f"{functionnsfw}", inline=False)
        setupembed71.add_field(name=f"Autorole", value=f"{functionautrole}", inline=False)
        setupembed71.add_field(name=f"Default role", value=f"---", inline=False)
        setupembed71.add_field(name=f"Ticket system", value=f"---", inline=False)
        setupembed71.add_field(name=f"Ticket channel", value=f"---", inline=False)
        setupembed71.add_field(name=f"Ticket category", value=f"---", inline=False)
        setupembed71.set_footer(text=f"Mention the default role you want to use")
        setupembed71.set_thumbnail(url=bot.user.avatar_url)
        await setupmsg.edit(embed=setupembed71)

        defrole: Message = await bot.wait_for("message", check=check)
        defrole_content = defrole.content
        await defrole.delete()
        defroleid = defrole_content.replace("<", "").replace("@", "").replace("&", "").replace(">", "")
        defintroleid = int(defroleid)
        actualdefrole: Role = discord.utils.get(ctx.guild.roles, id=defintroleid)
        functionautroledefrole = actualdefrole.mention
    if autrole_content == "no":
        functionautrole = "Disabled"
        functionautroledefrole = "-//-"

    setupembed8 = discord.Embed(title=f"Setup Configuration",
                                description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                color=discord.Color.purple())
    setupembed8.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
    setupembed8.add_field(name=f"Admin role", value=f"{actualrole.mention}", inline=False)
    setupembed8.add_field(name=f"Logs channel", value=f"{actual_logsc.mention}", inline=False)
    setupembed8.add_field(name=f"Music channel", value=f"{actual_musicc.mention}", inline=False)
    setupembed8.add_field(name=f"Bot's announcements", value=f"Disabled", inline=False)
    setupembed8.add_field(name=f"NSFW content", value=f"Disabled", inline=False)
    setupembed8.add_field(name=f"Autorole", value=f"{functionautrole}", inline=False)
    setupembed8.add_field(name=f"Default role", value=f"{functionautroledefrole}", inline=False)
    setupembed8.add_field(name=f"Ticket system", value=f"---", inline=False)
    setupembed8.add_field(name=f"Ticket channel", value=f"---", inline=False)
    setupembed8.add_field(name=f"Ticket category", value=f"---", inline=False)
    setupembed8.set_footer(text=f"Do you want to enable the ticket system? (yes / no)")
    setupembed8.set_thumbnail(url=bot.user.avatar_url)
    await setupmsg.edit(embed=setupembed8)

    ticketsystem: Message = await bot.wait_for("message", check=check)
    ticketsystem_content = ticketsystem.content
    await ticketsystem.delete()
    if ticketsystem_content == "yes":
        functionticketsystem = "Enabled"
        setupembed81 = discord.Embed(title=f"Setup Configuration",
                                     description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                     color=discord.Color.purple())
        setupembed81.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
        setupembed81.add_field(name=f"Admin role", value=f"{actualrole.mention}", inline=False)
        setupembed81.add_field(name=f"Logs channel", value=f"{actual_logsc.mention}", inline=False)
        setupembed81.add_field(name=f"Music channel", value=f"{actual_musicc.mention}", inline=False)
        setupembed81.add_field(name=f"Bot's announcements", value=f"Disabled", inline=False)
        setupembed81.add_field(name=f"NSFW content", value=f"Disabled", inline=False)
        setupembed81.add_field(name=f"Autorole", value=f"{functionautrole}", inline=False)
        setupembed81.add_field(name=f"Default role", value=f"{functionautroledefrole}", inline=False)
        setupembed81.add_field(name=f"Ticket system", value=f"{functionticketsystem}", inline=False)
        setupembed81.add_field(name=f"Ticket channel", value=f"---", inline=False)
        setupembed81.add_field(name=f"Ticket category", value=f"---", inline=False)
        setupembed81.set_footer(text=f"Mention the channel where tickets are created")
        setupembed81.set_thumbnail(url=bot.user.avatar_url)
        await setupmsg.edit(embed=setupembed81)

        ticketchannelmsg: Message = await bot.wait_for("message", check=check)
        ticketchannel_content = ticketchannelmsg.content
        await ticketchannelmsg.delete()
        ticketchannel_id = ticketchannel_content.replace("<", "").replace("#", "").replace("#", "").replace(">", "")
        actual_ticketchannel: TextChannel = discord.utils.get(ctx.guild.text_channels, id=int(ticketchannel_id))
        functionticketchannel = actual_ticketchannel.mention

        setupembed82 = discord.Embed(title=f"Setup Configuration",
                                     description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footero",
                                     color=discord.Color.purple())
        setupembed82.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
        setupembed82.add_field(name=f"Admin role", value=f"{actualrole.mention}", inline=False)
        setupembed82.add_field(name=f"Logs channel", value=f"{actual_logsc.mention}", inline=False)
        setupembed82.add_field(name=f"Music channel", value=f"{actual_musicc.mention}", inline=False)
        setupembed82.add_field(name=f"Bot's announcements", value=f"Disabled", inline=False)
        setupembed82.add_field(name=f"NSFW content", value=f"Disabled", inline=False)
        setupembed82.add_field(name=f"Autorole", value=f"{functionautrole}", inline=False)
        setupembed82.add_field(name=f"Default role", value=f"{functionautroledefrole}", inline=False)
        setupembed82.add_field(name=f"Ticket system", value=f"{functionticketsystem}", inline=False)
        setupembed82.add_field(name=f"Ticket channel", value=f"{functionticketchannel}", inline=False)
        setupembed82.add_field(name=f"Ticket category", value=f"---", inline=False)
        setupembed82.set_footer(text=f"Write the EXACT name of the category where tickets will go to")
        setupembed82.set_thumbnail(url=bot.user.avatar_url)
        await setupmsg.edit(embed=setupembed82)

        ticketcategorymsg: Message = await bot.wait_for("message", check=check)
        ticketcategory_content = ticketcategorymsg.content
        await ticketcategorymsg.delete()
        actualticketcategory: CategoryChannel = discord.utils.get(ctx.guild.categories, name=ticketcategory_content)
        functionticketcategory = actualticketcategory.name
    else:
        functionticketsystem = "Disabled"
        functionticketchannel = "-//-"
        functionticketcategory = "-//-"

    setupembed9 = discord.Embed(title=f"Setup Configuration",
                                description=f"This is the setup screen. Here you can see everything that was changed and what is going to be changed.\nFollow the steps in the footer",
                                color=discord.Color.purple())
    setupembed9.add_field(name=f"New prefix", value=f"{actualprefix}", inline=False)
    setupembed9.add_field(name=f"Admin role", value=f"{actualrole.mention}", inline=False)
    setupembed9.add_field(name=f"Logs channel", value=f"{actual_logsc.mention}", inline=False)
    setupembed9.add_field(name=f"Music channel", value=f"{actual_musicc.mention}", inline=False)
    setupembed9.add_field(name=f"Bot's announcements", value=f"Disabled", inline=False)
    setupembed9.add_field(name=f"NSFW content", value=f"Disabled", inline=False)
    setupembed9.add_field(name=f"Autorole", value=f"{functionautrole}", inline=False)
    setupembed9.add_field(name=f"Default role", value=f"{functionautroledefrole}", inline=False)
    setupembed9.add_field(name=f"Ticket system", value=f"{functionticketsystem}", inline=False)
    setupembed9.add_field(name=f"Ticket channel", value=f"{functionticketchannel}", inline=False)
    setupembed9.add_field(name=f"Ticket category", value=f"{functionticketcategory}", inline=False)
    setupembed9.set_footer(text=f"Commit changes? (yes / no)")
    setupembed9.set_thumbnail(url=bot.user.avatar_url)
    await setupmsg.edit(embed=setupembed9)

    # commitmsg: Message = await ctx.send(f"Commit Changes? (yes / no)")
    commit: Message = await bot.wait_for("message", check=check)
    commit_content = commit.content
    await commit.delete()
    if commit_content == "yes":
        apllyingmsg: Message = await ctx.send(f"Applying configuration...")
        try:
            set_prefix(ctx.guild, actualprefix)
            set_adminrole(ctx.guild, role=actualrole)
            set_logschannel(ctx.guild, channel=actual_logsc)
            set_musicchannel(ctx.guild, channel=actual_musicc)
            if announcements_content == "yes":
                set_announcements(ctx.guild, True)
            else:
                set_announcements(ctx.guild, False)
            if nsfw_content == "yes":
                set_porn(ctx.guild, True)
            else:
                set_porn(ctx.guild, False)
            if autrole_content == "yes":
                set_autorole(ctx.guild, True, actualdefrole)
            else:
                set_autorole(ctx.guild, False)
            if ticketsystem_content == "yes":
                set_ticketsystem(ctx.guild, True, actual_ticketchannel, actualticketcategory)
                ticketembed = discord.Embed(title="Ticket Creation",
                                            description=f"This is the ticket channel.\nYou can ask for staff's support by using `{get_prefix(ctx.guild)}ticket create`",
                                            color=discord.Color.dark_blue())
                await actual_ticketchannel.send(embed=ticketembed)
            else:
                set_ticketsystem(ctx.guild, False)

            await apllyingmsg.delete()
            await ctx.send(f"Configuration completed. Use `{get_prefix(ctx.guild)}help` to get a list of commands")
        except Exception as error:
            print(error)
            in_setup.remove(ctx.guild.id)
            return await ctx.send(f"Something went wrong while applying configurations")
    if commit_content == "no":
        await commitmsg.delete()
        set_setup(ctx.guild, False)
        in_setup.remove(ctx.guild.id)
        return await ctx.send(f"Setup process canceled.")

    set_setup(ctx.guild, True)
    in_setup.remove(ctx.guild.id)
    # await ctx.send(
    # f"Configuration finished. Remember you can re-configure anything it by using `{get_prefix(ctx.message.guild)}setup` again or using the respective commands")


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
    await ctx.send(f"Admin role changed to {role.mention}")

    fdate = datetime.now().strftime("%A, %B %d %Y @ %H:%M:%S %p")

    logsembed = discord.Embed(
        title="Admin role changed",
        colour=discord.Color.red()
    )

    logsembed.set_footer(text=f"{ctx.message.author.name}: {fdate}")
    logsembed.add_field(name="Role changed to", value=role.mention, inline=True)

    logschannel = discord.utils.get(ctx.guild.text_channels, id=get_logschannel(ctx))
    await logschannel.send(embed=logsembed)


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
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

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


@bot.command(name="ticket-system")
async def ticketsystemcommand(ctx):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    value = get_ticket(ctx.guild)

    def check(m):
        return m.author.id == ctx.author.id

    if not value:
        await ctx.send(
            f"Ticket System is now ENABLED.\nMention the channel where you want ticket-related commands to be used")
        channelmsg: Message = await bot.wait_for("message", check=check)
        channelmsgcontent = channelmsg.content
        channelid = channelmsgcontent.replace("<", "").replace("#", "").replace(">", "")
        intchannelid = int(channelid)
        actualchannel = discord.utils.get(ctx.guild.text_channels, id=intchannelid)

        await ctx.send(f"Great, now write the EXACT NAME of the category where you want new tickets to be created in")
        categorymsg: Message = await bot.wait_for("message", check=check)
        categoryname = categorymsg.content
        actualcategory = discord.utils.get(ctx.guild.categories, name=categoryname)

        set_ticketsystem(ctx.guild, True, actualchannel, actualcategory)

        ticketembed = discord.Embed(title="Ticket Creation",
                                    description=f"This is the ticket channel.\nYou can ask for staff's support by using `{get_prefix(ctx.guild)}ticket create`",
                                    color=discord.Color.dark_blue())
        await actualchannel.send(embed=ticketembed)
        await ctx.send(
            f"Ticket system is now Enabled.\nCommands channel: {actualchannel.mention}\nTickets Category: {actualcategory.name}")
    if value:
        await ctx.send(f"Ticket System is now DISABLED")
        set_ticketsystem(ctx.guild, False)
        return


@bot.command(name="setporn")
async def setporncommand(ctx):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    value = get_pornvalue(ctx.guild)

    if value:
        set_porn(ctx.guild, False)
        return await ctx.send(f"Porn feature is now disabled")
    elif not value:
        set_porn(ctx.guild, True)
        return await ctx.send(f"Porn feature is now enabled")


@bot.command(name="ticket")
async def ticketcommand(ctx, opt: str):
    data = get_ticketchannels(ctx.guild)
    if opt == "create":
        createchannelid = data["channelid"]
        createchannel: TextChannel = discord.utils.get(ctx.guild.text_channels, id=createchannelid)
        if not ctx.channel == createchannel:
            await ctx.send(f"You can only use kick commands in the tickets channel ({createchannel.mention})")
            return
        if not get_ticket(ctx.guild):
            msg: Message = await ctx.send(f"This server doesn't have the ticket system activated.")
            await ctx.message.delete()
            return await msg.delete(delay=5)

        if discord.utils.get(ctx.guild.text_channels, name=f"{ctx.author.name}-ticket") is not None:
            msg: Message = await ctx.send(f"You already have an open ticket. Please use it.")
            await ctx.message.delete()
            return await msg.delete(delay=5)

        creatingmsg: Message = await ctx.send(f"Ticket being created, please stand by...")
        categoryid = data["categoryid"]
        category = discord.utils.get(ctx.guild.categories, id=categoryid)
        ticketchannel: TextChannel = await ctx.guild.create_text_channel(name=f"{ctx.author.name}-ticket",
                                                                         category=category, overwrites={
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                ctx.author: discord.PermissionOverwrite(read_messages=True),
                discord.utils.get(ctx.guild.roles, id=get_adminrole(ctx.message)): discord.PermissionOverwrite(
                    read_messages=True)
            })
        ticketembed = discord.Embed(title=f"Here's your ticket {ctx.author.name}",
                                    description=f"Tell us what's your problem and we will try to solve it.",
                                    color=discord.Color.blue())
        ticketembed.set_footer(text=f"When the problem has been solved use {get_prefix(ctx.guild)}ticket close")
        await ticketchannel.send(content=ctx.author.mention, embed=ticketembed)
        await creatingmsg.delete()
        await ctx.message.delete()

        fdate = datetime.now().strftime("%A, %B %d %Y @ %H:%M:%S %p")

        logsembed = discord.Embed(title="A ticket has been created", color=discord.Color.blue())
        logsembed.add_field(name="Ticket", value=ticketchannel.mention)
        logsembed.set_footer(text=f"{ctx.author.name}: {fdate}", icon_url=ctx.author.avatar_url)
        logschannelid = get_logschannel(ctx.message)
        logschannel: TextChannel = discord.utils.get(ctx.guild.text_channels, id=logschannelid)
        await logschannel.send(embed=logsembed)
        return

    if opt == "close":
        admin_role_id = get_adminrole(ctx)
        if ctx.author not in ctx.guild.get_role(admin_role_id).members:
            if not get_ticket(ctx.guild):
                msg: Message = await ctx.send(f"This server doesn't have the ticket system activated.")
                await ctx.message.delete()
                return await msg.delete(delay=5)

            channel: TextChannel = ctx.channel
            if not "-ticket" in channel.name:
                msg: Message = await ctx.send(f"There's no ticket here to be closed")
                return msg.delete(delay=5)

            if channel.name != f"{ctx.author.name.lower()}-ticket":
                msg: Message = await ctx.send(f"You can't close a ticket that isn't yours")
                return await msg.delete(delay=5)

            channel: TextChannel = ctx.channel
            await ctx.send(f"Ticket will be closed in 5 seconds")
            await asyncio.sleep(5)
            await channel.set_permissions(ctx.author, read_messages=False)
            await channel.edit(name=f"{ctx.author.name}-closed")

            fdate = datetime.now().strftime("%A, %B %d %Y @ %H:%M:%S %p")
            logsembed = discord.Embed(title=f"Ticket closed", description=f"A ticket has been closed",
                                      color=discord.Color.dark_orange())
            logsembed.add_field(name=f"Ticket", value=ctx.channel.mention)
            logsembed.set_footer(text=f"{ctx.author.name}: {fdate}", icon_url=ctx.author.avatar_url)
            logschannelid = get_logschannel(ctx.message)
            logschannel = discord.utils.get(ctx.guild.text_channels, id=logschannelid)
            await logschannel.send(embed=logsembed)
            return await ctx.send(f"Ticket closed")

        else:
            if not get_ticket(ctx.guild):
                msg: Message = await ctx.send(f"This server doesn't have the ticket system activated.")
                await ctx.message.delete()
                return await msg.delete(delay=5)

            channel: TextChannel = ctx.channel
            if not "-ticket" in channel.name:
                msg: Message = await ctx.send(f"There's no ticket here to be closed")
                return msg.delete(delay=5)

            channel: TextChannel = ctx.channel
            await ctx.send(f"Ticket will be closed in 5 seconds")
            await asyncio.sleep(5)
            await channel.set_permissions(ctx.author, read_messages=False)
            await channel.edit(name=f"{ctx.author.name}-closed")
            await ctx.send(f"Ticket closed")
            return
    if opt == "delete":
        admin_role_id = get_adminrole(ctx)
        if ctx.author not in ctx.guild.get_role(admin_role_id).members:
            return await ctx.send(f"Only staff members can delete tickets")

        if not "-closed" in ctx.channel.name:
            return await ctx.send(f"There's no ticket here to be deleted")

        await ctx.send(f"Ticket will be deleted in 5 seconds")
        await asyncio.sleep(5)
        fdate = datetime.now().strftime("%A, %B %d %Y @ %H:%M:%S %p")
        logsembed = discord.Embed(title=f"Ticket deleted", description=f"A ticket has been deleted",
                                  color=discord.Color.red())
        logsembed.add_field(name=f"Ticket", value=ctx.channel.name)
        logsembed.set_footer(text=f"{ctx.author.name}: {fdate}", icon_url=ctx.author.avatar_url)
        logschannelid = get_logschannel(ctx.message)
        logschannel = discord.utils.get(ctx.guild.text_channels, id=logschannelid)
        await logschannel.send(embed=logsembed)
        return await ctx.channel.delete()


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
            try:
                logschannel = discord.utils.get(guild.text_channels, id=get_globallogschannel(guild))
                embed = discord.Embed(title="GLOBAL ANNOUNCEMENT",
                                      description=message.replace("$guild_prefix", get_prefix(guild)),
                                      color=discord.Colour.purple())
                await logschannel.send(embed=embed)
                print(f"Global message sent to {guild.name} (id: {guild.id})")
            except Exception as err:
                print(f"Couldn't send announcement to guild {guild.name}. Reason: {err}")
                continue


@bot.command(name="help")
async def helpcommand(ctx, page: int = 0):
    if page == 0:
        helpembed0 = discord.Embed(title='Help Menu', description='Choose one of the categories',
                                   colour=discord.Color.dark_green())
        helpembed0.set_footer(text="Categories")
        helpembed0.add_field(name="User commands", value=f"{get_prefix(ctx.guild)}help 1", inline=False)

        helpembed0.add_field(name='Music Commands', value=f"{get_prefix(ctx.guild)}help 2", inline=False)

        helpembed0.add_field(name='Admin Commands', value=f"{get_prefix(ctx.guild)}help 3", inline=False)

        if get_pornvalue(ctx.guild):
            helpembed0.add_field(name='Porn Commands', value=f"{get_prefix(ctx.guild)}help 4", inline=False)
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
                             value=f"Gets a cute photo, gif or video.", inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}server",
                             value=f"Show information about the server.", inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}info <user>",
                             value=f"Show information about the specified user.", inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}ticket [option]",
                             value=f"Ticket system command: Use option `create` to create a ticket and `close` to close.",
                             inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}invites <user>",
                             value=f"Gets the number of invites the user has. (Only counts those after the bot was added)",
                             inline=False)
        helpembed1.add_field(name=f"{get_prefix(ctx.guild)}invite-leaderboard",
                             value=f"Shows the top 5 inviters of the server (Only counts invites after the bot was added)",
                             inline=False)
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
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music shuffle",
                             value="Shuffles the musics in the queue", inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music repeat",
                             value="Keeps repeating all musics in queue in a loop", inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music lyrics <music>",
                             value="Gets the lyrics of the specified music", inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music volume <volume> (Unavailable)",
                             value="Changes the volume of the music (Recomended: 10%)", inline=False)
        helpembed2.add_field(name=f"{get_prefix(ctx.guild)}music set-playlist (Admin only)",
                             value="Sets the current queue to the server playlist", inline=False)

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
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}ticket-system", value="Enables / disables the ticket system",
                             inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}set-joinmessage",
                             value="Enables / disables the join message. If being enabled you can choose in which channel messages are sent and what message you want to send",
                             inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}set-leavemessage",
                             value="Enables / disables the leave message. If being enabled you can choose in which channel messages are sent and what message you want to send",
                             inline=False)
        helpembed3.add_field(name=f"{get_prefix(ctx.guild)}setup",
                             value="First command to execute when bot joins the server. Configures everything that is "
                                   "needed",
                             inline=False)

        await ctx.send(embed=helpembed3)

    if page == 4:
        if not get_pornvalue(ctx.guild):
            return await ctx.send(f"This help page is disabled in this server")
        helpembed4 = discord.Embed(title="Help Menu", description="These are the commands relative to porn",
                                   colour=discord.Color.from_rgb(255, 51, 153))
        helpembed4.set_footer(text="Porn commands")

        helpembed4.add_field(name=f"{get_prefix(ctx.guild)}porn ass", value="Gets a pic of an ass",
                             inline=False)
        helpembed4.add_field(name=f"{get_prefix(ctx.guild)}porn balls", value="Gets a pic of some balls",
                             inline=False)
        helpembed4.add_field(name=f"{get_prefix(ctx.guild)}porn boobs",
                             value="Gets a pic of a pair of boobs", inline=False)
        helpembed4.add_field(name=f"{get_prefix(ctx.guild)}porn dick", value="Gets a pic of a dick",
                             inline=False)
        helpembed4.add_field(name=f"{get_prefix(ctx.guild)}porn gay", value="Gets a pic or gif of a gay video",
                             inline=False)
        helpembed4.add_field(name=f"{get_prefix(ctx.guild)}porn lesbian", value="Gets a pic or gif of a lesbian video",
                             inline=False)
        helpembed4.add_field(name=f"{get_prefix(ctx.guild)}porn pussy",
                             value="Gets a pic of a pussy", inline=False)
        helpembed4.add_field(name=f"{get_prefix(ctx.guild)}porn sex",
                             value="Gets a pic or gif of a porn video", inline=False)

        await ctx.send(embed=helpembed4)


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


@bot.command(name="invites")
async def invitescommand(ctx, member: Member):
    return await ctx.send(
        f"User {member.mention} has {get_user_invites(ctx.guild, member)} invite{'' if get_user_invites(ctx.guild, member) == 1 else 's'}!")


@bot.command(name="set-joinmessage")
async def setjoinmessagecommand(ctx, message: str = None):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    if get_joinvalue(ctx.guild):
        set_join_message(ctx.guild, False)
        return await ctx.send(f"Join messages disabled!")

    def check(m):
        return m.author.id == ctx.author.id

    joinmessageembed = discord.Embed(title=f"Join Messages enabled",
                                     description=f"Join messages happen when a new user enters the server.",
                                     color=discord.Color.purple())
    joinmessageembed.add_field(name=f"Greetings Channel", value=f"---", inline=False)
    joinmessageembed.add_field(name=f"Greetings Message", value=f"---", inline=False)
    joinmessageembed.set_footer(text=f"Mention the channel where you want the message to be displayed")
    sent_joinmessageembed: Message = await ctx.send(embed=joinmessageembed)

    channelmsg = await bot.wait_for("message", check=check)
    channelmsg_content = channelmsg.content
    await channelmsg.delete()
    joinchannel_id = channelmsg_content.replace("<", "").replace("#", "").replace("#", "").replace(">", "")
    actual_joinchannel: TextChannel = discord.utils.get(ctx.guild.text_channels, id=int(joinchannel_id))

    joinmessageembed = discord.Embed(title=f"Join Messages enabled",
                                     description=f"Join messages happen when a new user enters the server.",
                                     color=discord.Color.purple())
    joinmessageembed.add_field(name=f"Greetings Channel", value=actual_joinchannel.mention, inline=False)
    joinmessageembed.add_field(name=f"Greetings Message", value=f"---", inline=False)
    joinmessageembed.set_footer(
        text=f"Write the message you want to be displayed when a user enters. You can see a list of vairables using {get_prefix(ctx.guild)}variables")
    await sent_joinmessageembed.edit(embed=joinmessageembed)
    while True:
        messagemsg: Message = await bot.wait_for("message", check=check)
        if messagemsg.content == f"{get_prefix(ctx.guild)}variables":
            await messagemsg.delete()
            variablesembed = discord.Embed(title=f"Variables List",
                                           description=f"This is a list of all variables that can be used in your join / leave messages",
                                           colour=discord.Colour.purple())
            variablesembed.add_field(name=f"$server_name", value=f"Writes the name of the server", inline=False)
            variablesembed.add_field(name=f"$user_name", value=f"Writes the name of the User that entered the server",
                                     inline=False)
            variablesembed.add_field(name=f"$user_mention", value=f"Mentions the User that entered the server",
                                     inline=False)
            variablesembed.add_field(name=f"$inviter_name",
                                     value=f"Writes the name of the User that invited the new User", inline=False)
            variablesembed.add_field(name=f"$inviter_mention", value=f"Mentions the User that invited the new User",
                                     inline=False)
            variablesembed.add_field(name=f"$invite_code",
                                     value=f"Writes the code of the invite used to enter the server (Ex: 6azqqNb)",
                                     inline=False)
            variablesembed.add_field(name=f"$invite_link",
                                     value=f"Writes the link of the invite used to enter the server\n(Ex: https://discord.gg/6azqqNb)",
                                     inline=False)
            variablesembed.add_field(name=f"$invites_number",
                                     value=f"Writes the number of invites that the User who invited the new User has",
                                     inline=False)
            variablesembed.set_footer(
                text=f"Use this variables in your message to replace them with the corresponding value")
            await ctx.send(embed=variablesembed)
        else:
            break
    messagemsg_content = messagemsg.content
    await messagemsg.delete()
    set_join_message(ctx.guild, True, actual_joinchannel, emoji.demojize(messagemsg_content))
    return await ctx.send(f"Join channel and message set.")


@bot.command(name="set-leavemessage")
async def setleavemessagecommand(ctx):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    if get_leavevalue(ctx.guild):
        set_leave_message(ctx.guild, False)
        return await ctx.send(f"Leave messages disabled!")

    def check(m):
        return m.author.id == ctx.author.id

    leavemessageembed = discord.Embed(title=f"Leave Messages enabled",
                                      description=f"Leave messages happen when a user leaves the server.",
                                      color=discord.Color.purple())
    leavemessageembed.add_field(name=f"Goodbye Channel", value=f"---", inline=False)
    leavemessageembed.add_field(name=f"Goodbye Message", value=f"---", inline=False)
    leavemessageembed.set_footer(text=f"Mention the channel where you want the message to be displayed")
    sent_leavemessageembed: Message = await ctx.send(embed=leavemessageembed)

    channelmsg = await bot.wait_for("message", check=check)
    channelmsg_content = channelmsg.content
    await channelmsg.delete()
    leavechannel_id = channelmsg_content.replace("<", "").replace("#", "").replace("#", "").replace(">", "")
    actual_leavechannel: TextChannel = discord.utils.get(ctx.guild.text_channels, id=int(leavechannel_id))

    leavemessageembed = discord.Embed(title=f"Join Messages enabled",
                                      description=f"Join messages happen when a new user enters the server.",
                                      color=discord.Color.purple())
    leavemessageembed.add_field(name=f"Goodbye Channel", value=actual_leavechannel.mention, inline=False)
    leavemessageembed.add_field(name=f"Goodbye Message", value=f"---", inline=False)
    leavemessageembed.set_footer(
        text=f"Write the message you want to be displayed when a user enters. You can see a list of vairables using {get_prefix(ctx.guild)}variables")
    await sent_leavemessageembed.edit(embed=leavemessageembed)
    while True:
        messagemsg: Message = await bot.wait_for("message", check=check)
        if messagemsg.content == f"{get_prefix(ctx.guild)}variables":
            await messagemsg.delete()
            variablesembed = discord.Embed(title=f"Variables List",
                                           description=f"This is a list of all variables that can be used in your join / leave messages",
                                           colour=discord.Colour.purple())
            variablesembed.add_field(name=f"$server_name", value=f"Writes the name of the server", inline=False)
            variablesembed.add_field(name=f"$user_name", value=f"Writes the name of the User that left the server",
                                     inline=False)
            variablesembed.add_field(name=f"$user_mention", value=f"Mentions the User that left the server",
                                     inline=False)
            variablesembed.add_field(name=f"$inviter_name",
                                     value=f"Writes the name of the User that invited the new User", inline=False)
            variablesembed.add_field(name=f"$inviter_mention", value=f"Mentions the User that invited the old User",
                                     inline=False)
            variablesembed.add_field(name=f"$invite_code",
                                     value=f"Writes the code of the invite used to enter the server (Ex: 6azqqNb)",
                                     inline=False)
            variablesembed.add_field(name=f"$invite_link",
                                     value=f"Writes the link of the invite used to enter the server\n(Ex: https://discord.gg/6azqqNb)",
                                     inline=False)
            variablesembed.add_field(name=f"$invites_number",
                                     value=f"Writes the number of invites that the User who invited the old User has",
                                     inline=False)
            variablesembed.set_footer(
                text=f"Use this variables in your message to replace them with the corresponding value")
            await ctx.send(embed=variablesembed)
        else:
            break
    messagemsg_content = messagemsg.content
    await messagemsg.delete()
    set_leave_message(ctx.guild, True, actual_leavechannel, emoji.demojize(messagemsg_content))
    return await ctx.send(f"Leave channel and message set.")


@bot.command(name="invite-leaderboard")
async def inviteleaderboardcommand(ctx):
    inviteslist: list = get_inviteleaderboard(ctx.guild)
    # print(inviteslist)
    top: dict = {}
    i = 0
    for user in inviteslist:
        if i == 5:
            break
        actualuser: Member = discord.utils.get(ctx.guild.members, id=user[0])
        top[actualuser] = user[1]
        i = i + 1
    # print(top)
    topembed = discord.Embed(title=f"Top Inviters", color=discord.Color.purple())
    i2 = 0
    for member in top:
        if i2 == 0:
            topembed.description = f"#{i2 + 1} - **{member.name}** with **{top[member]}** invites"
        else:
            topembed.description = f"{topembed.description}\n#{i2 + 1} - **{member.name}** with **{top[member]}** invites"
        i2 = i2 + 1

    return await ctx.send(embed=topembed)


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
    imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    videoval = jsonfile[0]['data']['children'][0]['data']['is_video']
    if videoval or not ".jpg" in str(imgurl) and not ".gif" in str(imgurl) or ".gifv" in str(imgurl):
        await awwcommand(ctx)
        return

    memeembed = discord.Embed(color=discord.Color.greyple())
    memeembed.set_image(url=imgurl)
    memeembed.set_footer(text=f"Cuteness requested by {ctx.author.name} from r/{str(subreddit)}")
    await ctx.send(embed=memeembed)


@bot.command(name="porn")
async def porncommand(ctx, *, arg):
    if not get_pornvalue(ctx.guild):
        return await ctx.send(f"This command is disabled in this server.")

    channel: TextChannel = ctx.channel
    if not channel.is_nsfw():
        return await ctx.send(f"This command can't be used in non-NSFW channels")

    if arg == "pussy":
        subreddit = reddit.subreddit("pussy")
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/pussy/comments/{submission}/.json"
        try:
            # urllib.request.urlretrieve(posturl, f'reddit_jsons/{submission}.json')
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
            jsonfile = r.json()
        except Exception:
            await ctx.send(f"There was a problem getting the pussy... Try again later")
            return

        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    if arg == "boobs":
        subreddit = reddit.subreddit("boobs")
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/boobs/comments/{submission}/.json"
        try:
            # urllib.request.urlretrieve(posturl, f'reddit_jsons/{submission}.json')
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
            jsonfile = r.json()
        except Exception:
            await ctx.send(f"There was a problem getting the boobs... Try again later")
            return

        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    if arg == "dick":
        subreddit = reddit.subreddit("cock")
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/cock/comments/{submission}/.json"
        try:
            # urllib.request.urlretrieve(posturl, f'reddit_jsons/{submission}.json')
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
            jsonfile = r.json()
        except Exception:
            await ctx.send(f"There was a problem getting the dick... Try again later")
            return

        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    if arg == "balls":
        subreddit = reddit.subreddit("balls")
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/balls/comments/{submission}/.json"
        try:
            # urllib.request.urlretrieve(posturl, f'reddit_jsons/{submission}.json')
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
            jsonfile = r.json()
        except Exception:
            await ctx.send(f"There was a problem getting the balls... Try again later")
            return

        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    if arg == "ass":
        subreddit = reddit.subreddit("ass")
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/ass/comments/{submission}/.json"
        try:
            # urllib.request.urlretrieve(posturl, f'reddit_jsons/{submission}.json')
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
            jsonfile = r.json()
        except Exception:
            await ctx.send(f"There was a problem getting the ass... Try again later")
            return

        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    if arg == "sex":
        sublist = ["porn", "PornGifs"]
        sub = random.choice(sublist)
        subreddit = reddit.subreddit(sub)
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/{sub}/comments/{submission}/.json"
        try:
            # urllib.request.urlretrieve(posturl, f'reddit_jsons/{submission}.json')
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
            jsonfile = r.json()
        except Exception:
            await ctx.send(f"There was a problem getting the porn... Try again later")
            return

        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    if arg == "gay":
        sublist = ["gayporn", "GayGifs"]
        sub = random.choice(sublist)
        subreddit = reddit.subreddit(sub)
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/{sub}/comments/{submission}/.json"
        try:
            # urllib.request.urlretrieve(posturl, f'reddit_jsons/{submission}.json')
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
            jsonfile = r.json()
        except Exception:
            await ctx.send(f"There was a problem getting the porn... Try again later")
            return

        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    if arg == "lesbian":
        sublist = ["Lesbian_gifs", "lesbians"]
        sub = random.choice(sublist)
        subreddit = reddit.subreddit(sub)
        submission = subreddit.random()
        posturl = f"https://www.reddit.com/r/{sub}/comments/{submission}/.json"
        try:
            # urllib.request.urlretrieve(posturl, f'reddit_jsons/{submission}.json')
            r = requests.get(posturl, headers={'User-agent': 'Mozilla/5.0'})
            jsonfile = r.json()
        except Exception:
            await ctx.send(f"There was a problem getting the porn... Try again later")
            return

        imgurl = jsonfile[0]['data']['children'][0]['data']['url']

    videoval = jsonfile[0]['data']['children'][0]['data']['is_video']
    if videoval or not ".jpg" in str(imgurl) and not ".gif" in str(imgurl) or ".gifv" in str(imgurl):
        await porncommand(ctx, arg=arg)
        return

    pornembed = discord.Embed(title="",
                              color=discord.Color.greyple())
    pornembed.set_image(url=imgurl)
    pornembed.set_footer(text=f"Porn requested by {ctx.author.name}")
    await ctx.send(embed=pornembed)


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


# @bot.command(name="ticketchannels")
# async def ticketchannels(ctx):
#     channels = get_ticketchannels(ctx.guild)
#     channelid = channels["channelid"]
#     categoryid = channels["categoryid"]
#     channel: TextChannel = discord.utils.get(ctx.guild.text_channels, id=channelid)
#     category: Category = discord.utils.get(ctx.guild.categories, id=categoryid)
#     await ctx.send(f"Channel: {channel.mention}\nCategory: {category}")

atexit.register(exiting)
bot.run(TOKEN)
