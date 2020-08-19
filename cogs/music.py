import asyncio
import sys

import discord
import lavalink
import mysql.connector as mysql
from discord import Guild
from discord import TextChannel
from discord import User
from discord.ext import commands
from discord.ext.tasks import loop

# from bot import get_musicchannel
# from bot import get_prefix
# from bot import mycursor

mydb = None
mycursor = None


# Connect to mysql
def connect_mysql():
    global mydb
    global mycursor
    try:
        mydb = mysql.connect(
            host="{IP}",
            user="{user}",
            password="{password}",
            database="{db}"
        )
        print(f"Music Connected to database")
    except mysql.Error:
        sys.exit(f"Couldn't establish connection to mysql server")

    mycursor = mydb.cursor()


@loop(count=None)
async def keep_mysql():
    while True:
        # keepalive = "SELECT * FROM prefixes"
        # mycursor.execute(keepalive)
        # result = mycursor.fetchall()
        # print("Keeping mysql connection alive")
        # await asyncio.sleep(180)
        mycursor.close()
        connect_mysql()
        await asyncio.sleep(180)


def get_musicchannel(guild: Guild):
    # with open("cogs/music.json") as f:
    #     channels = json.load(f)
    # channel: TextChannel = discord.utils.get(guild.text_channels, id=channels[str(guild.id)])
    # return channel.id
    sqlcommand = "SELECT channelid FROM musicchannels WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strchannelid = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    channelid = int(strchannelid)
    return channelid


def get_idmusicchannel(guildid: int):
    sqlcommand = "SELECT channelid FROM musicchannels WHERE guildid = %s"
    vals = (guildid,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strchannelid = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    channelid = int(strchannelid)
    return channelid


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        # self.bot.music.add_node("{ip}", 2333, '{pass}', 'eu', 'music-node')
        self.bot.music.add_node("localhost", 7000, 'server-utils', 'eu', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)

    @commands.command(name="music")
    async def music(self, ctx, opt, *, arg=None):
        if ctx.message.channel.id != get_musicchannel(ctx.guild):
            # channel = get_musicchannel(ctx.guild)
            actual_channel = discord.utils.get(ctx.guild.text_channels, id=get_musicchannel(ctx.guild))
            return await ctx.send(f"Music commands can only be used in the music channel ({actual_channel.mention})")
        if opt == "join":
            member = discord.utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
            if member is not None and member.voice is not None:
                vc = member.voice.channel
                player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
                if not player.is_connected:
                    player.store('channel', ctx.guild.id)
                    await self.connect_to(ctx.guild.id, str(vc.id))
        if opt == "play" and arg is not None:
            try:
                member = discord.utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
                if member is not None and member.voice is not None:
                    vc = member.voice.channel
                    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
                    if not player.is_connected:
                        player.store('channel', ctx.guild.id)
                        await self.connect_to(ctx.guild.id, str(vc.id))
                player = self.bot.music.player_manager.get(ctx.guild.id)
                query = f'ytsearch:{arg}'
                results = await player.node.get_tracks(query)
                tracks = results['tracks'][0:5]
                i = 0
                query_result = ''
                for track in tracks:
                    i = i + 1
                    query_result = query_result + f'{i}) {track["info"]["title"]}\n'
                embed = discord.Embed()
                embed.description = query_result
                embed.set_footer(text=f"Write down the number of the track you want")

                await ctx.channel.send(embed=embed)

                def check(m):
                    return m.author.id == ctx.author.id

                reponse = await self.bot.wait_for('message', check=check)
                track = tracks[int(reponse.content) - 1]

                player.add(requester=ctx.author.id, track=track)
                if not player.is_playing:
                    await player.play()
                    # await ctx.send(f"Started playing `{track['info']['title']}`")
                    return
                await ctx.send(f"Track `{track['info']['title']}` added to the queue")
            except Exception as error:
                print(error)

        if opt == "stop":
            try:
                player = self.bot.music.player_manager.get(ctx.guild.id)
                if player.is_playing:
                    await player.stop()
            except Exception as error:
                print(error)

        if opt == "volume" and arg is not None:
            if not ctx.author.id == 285084565469528064:
                creator: User = await self.bot.fetch_user(285084565469528064)
                await ctx.send(
                    f"This is a work in progress, therefore it can't be used except by my BEAUTIFUL creator "
                    f"{creator.display_name}")
                return
            try:
                player = self.bot.music.player_manager.get(ctx.guild.id)
                await player.set_volume(int(arg) * 10)
            except Exception as error:
                print(error)

        if opt == "pause":
            try:
                player = self.bot.music.player_manager.get(ctx.guild.id)
                await player.set_pause(True)
                await ctx.send(f"Music paused!")
            except Exception as error:
                print(error)

        if opt == "resume":
            try:
                player = self.bot.music.player_manager.get(ctx.guild.id)
                await player.set_pause(False)
                await ctx.send(f"Music resumed")
            except Exception as error:
                print(error)

        if opt == "leave":
            player = self.bot.music.player_manager.get(ctx.guild.id)
            if player.is_playing:
                await player.stop()
            await self.connect_to(ctx.guild.id, None)

        if opt == "skip":
            player = self.bot.music.player_manager.get(ctx.guild.id)
            await player.skip()
            await ctx.send(f"Track skipped")

        if opt == "queue":
            player = self.bot.music.player_manager.get(ctx.guild.id)
            embed = discord.Embed(title="Current Queue", description="The top one will play "
                                                                     "first\n-----------------------------",
                                  color=discord.Colour.darker_grey())
            i = 0
            for track in player.queue:
                i = i + 1
                embed.description = f"{embed.description}\n{i}) {track.title}"
            await ctx.send(embed=embed)
        # else:
        #     return await ctx.send(f"Subcommand unknown.")

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
            guild_id = int(event.player.guild_id)
            channelid: int = get_idmusicchannel(guild_id)
            guild: Guild = discord.utils.get(self.bot.guilds, id=guild_id)
            channel: TextChannel = discord.utils.get(guild.text_channels, id=channelid)
            channel.send(f"Player disconnect because queue ended")

        if isinstance(event, lavalink.events.TrackStartEvent):
            guild_id = int(event.player.guild_id)
            channelid: int = get_idmusicchannel(guild_id)
            guild: Guild = discord.utils.get(self.bot.guilds, id=guild_id)
            channel: TextChannel = discord.utils.get(guild.text_channels, id=channelid)
            track = event.track
            asyncio.sleep(2)
            await channel.send(f"Now playing `{track.title}`")

    async def connect_to(self, guild_id: int, channel_id: int):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    async def disconnect_from(self, guild_id: int):
        ws = self.bot._connection.voice_clients
        print(ws)


def setup(bot):
    connect_mysql()
    keep_mysql.start()
    bot.add_cog(Music(bot))
