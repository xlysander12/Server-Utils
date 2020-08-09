import os
import random
from dotenv import load_dotenv
import discord

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


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
@commands.has_role('Absolute Admin')
async def create_channel(ctx, channel_category, channel_name):
    guild = ctx.guild
    existing_category = discord.utils.get(guild.categories, name=channel_category)
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_category:
        print("Creating new category: " + channel_category)
        await guild.create_category(channel_category)
    if not existing_channel:
        print("Creating a new channel: " + channel_name)
        await guild.create_text_channel(channel_name, category=discord.utils.get(guild.categories, name=channel_category))


bot.run(TOKEN)
