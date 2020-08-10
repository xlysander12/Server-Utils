import json
import os
import random
from datetime import date
from datetime import datetime

import discord
from discord import Member
from discord import Role
from discord import TextChannel
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


# Connected

def get_prefix(client, message):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


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


bot = commands.Bot(command_prefix=get_prefix)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


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

    with open("logs.json") as f:
        channels = json.load(f)
    channels.pop(str(guild.id))

    with open("logs.json", 'w') as f:
        json.dump(channels, f, indent=4)


@bot.command(name='random', help="Responds with a random number beetween a and b")
async def nine_nine(ctx):
    response = random.randint(0, 100)
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
        print("Creating new category: " + channel_category)
        await guild.create_category(channel_category)
    if not existing_channel:
        print("Creating a new channel: " + channel_name)
        await guild.create_text_channel(channel_name,
                                        category=discord.utils.get(guild.categories, name=channel_category))


@bot.command(name="changeprefix", help="Choose the prefix for your server")
async def changeprefix(ctx, prefix):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return

    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open("prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send("Prefix changed to " + prefix)


@bot.command(name="changeadminrole", help="Choose the role that can execute admin commands")
@commands.has_guild_permissions(administrator=True)
async def changeadmin(ctx, *, role: Role):
    with open("admins.json", 'r') as f:
        admins = json.load(f)

    admins[str(ctx.guild.id)] = role.id

    with open("admins.json", 'w') as f:
        json.dump(admins, f, indent=4)

    await ctx.send(f"Admin role changed to {role.mention}")


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

    await ctx.send(f"User {target} was kicked from the server")


bot.run(TOKEN)
