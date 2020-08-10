import json
import os
import random

import discord
from discord import Member
from discord import Role
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


bot = commands.Bot(command_prefix=get_prefix)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print(get_adminrole)
    print(get_prefix)


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
@commands.has_role(get_adminrole)
async def create_channel(ctx, channel_category, channel_name):
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
@commands.has_role(get_adminrole)
async def changeprefix(ctx, prefix):
    with open("prefixes.json", 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open("prefixes.json", 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send("Prefix changed to " + prefix)


@bot.command(name="changeadminrole", help="Choose the role that can execute admin commands")
async def changeadmin(ctx, *, role: Role):
    with open("admins.json", 'r') as f:
        admins = json.load(f)

    admins[str(ctx.guild.id)] = role.id

    with open("admins.json", 'w') as f:
        json.dump(admins, f, indent=4)

    await ctx.send(f"Admin role changed to {role.mention}")


@bot.command(name="kick", help="Kicks a member from the server")
async def kickmember(ctx, target: Member, *, reason="None"):
    admin_role_id = get_adminrole(ctx)
    if ctx.author not in ctx.guild.get_role(admin_role_id).members:
        await ctx.send("You are not an admin!")
        return
    invite = await ctx.channel.create_invite()
    channel = await target.create_dm()
    # await channel.send("You have been kicked from the server " + ctx.guild.name)
    # await channel.send("With the following reason: " + reason)
    # await channel.send(f"Kicked by: {ctx.message.author.name}")
    # await channel.send(f"Consider this as an warning... You can re-enter the server here: {invite}")

    embed = discord.Embed(
        title="You have been kicked",
        colour=discord.Color.orange()
    )

    embed.set_footer(text="Server Utils Bot")
    embed.add_field(name='You have been kicked from the server', value=ctx.guild.name, inline=True)
    embed.add_field(name='Reason of the kick', value=reason, inline=True)
    embed.add_field(name='You were kicked by', value=ctx.message.author.name, inline=False)
    embed.add_field(name='Consider yourself warned... You can re-enter here', value=invite, inline=True)
    # await channel.send(f"You have been kicked from the server {ctx.guild.name}\n"
    # f"With the following reason: {reason}\n"
    # f"Kicked by: {ctx.message.author.name}\n"
    # f"Consider this as an warning... You can re-enter the server here: {invite}")

    await channel.send(embed=embed)
    await target.kick(reason=reason)
    await ctx.send(f"User {target} was kicked from the server")


@bot.command(name='ban', help="Bans a member from the server", category="Administration")
@commands.has_role(get_adminrole)
async def banmember(ctx, target: Member, reason='None'):
    channel = await target.create_dm()
    embed = discord.Embed(
        title="You have been banned",
        colour=discord.Color.red()
    )

    embed.set_footer(text="Server Utils Bot")
    embed.add_field(name="You have been BANNED from the server", value=ctx.guild.name, inline=False)
    embed.add_field(name='Reason of the ban', value=reason, inline=True)
    embed.add_field(name="You were banned by", value=ctx.message.author.name, inline=True)

    await channel.send(embed=embed)
    await target.ban(reason=reason)
    await ctx.send(f"User {target} was banned from the server")


bot.run(TOKEN)
