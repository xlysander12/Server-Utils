import asyncio
import atexit
import re

import discord
import lavalink
import lyricsgenius
import mysql.connector as mysql
from discord import Guild
from discord import Message
from discord import TextChannel
from discord import User
from discord import VoiceChannel
from discord.ext import commands
from discord.ext.tasks import loop

# from bot import get_musicchannel
# from bot import get_prefix
# from bot import mycursor

mydb = None
mycursor = None
genius = None
in_shuffle = dict()
in_repeat = dict()
current_track = dict()


# Connect to mysql
def connect_mysql():
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
            print(f"Music Connected to database")
            break
        except mysql.Error as error:
            print(f"Couldn't establish connection to mysql server. Reason: {error}")
            continue

    mycursor = mydb.cursor()


@loop(count=None)
async def keep_mysql():
    while True:
        global mydb
        global mycursor
        # keepalive = "SELECT * FROM prefixes"
        # mycursor.execute(keepalive)
        # result = mycursor.fetchall()
        # print("Keeping mysql connection alive")
        # await asyncio.sleep(180)
        if mydb is not None:
            mycursor.close()
        connect_mysql()
        await asyncio.sleep(180)


def genius():
    global genius
    genius = lyricsgenius.Genius("[ACCESS TOKEN]")


def exiting():
    global mycursor
    global mydb
    if mydb is not None:
        mycursor.close()
        print(f"Music disconnected from database")


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


def get_song(name):
    global genius
    music = dict()
    # musicname = None
    # artist = None
    # lyrics = None
    i = 0
    while True:
        try:
            if i == 7:
                music = None
                return music
            song = genius.search_song(name)
            lyrics = song.lyrics
            musicname = song.title
            artist = song.artist
        except Exception:
            i = i + 1
            continue
        break
    music["name"] = musicname
    music["artist"] = artist
    music["lyrics"] = lyrics
    return music


def get_idmusicchannel(guildid: int):
    sqlcommand = "SELECT channelid FROM musicchannels WHERE guildid = %s"
    vals = (guildid,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    strchannelid = str(result[0]).replace("(", "").replace(")", "").replace(",", "")
    channelid = int(strchannelid)
    return channelid


def set_serverplaylist(guild: Guild, playlist):
    checksqlcommand = "SELECT * FROM server_playlists WHERE guildid = %s"
    checkvals = (guild.id,)
    mycursor.execute(checksqlcommand, checkvals)
    result = mycursor.fetchall()

    if not result:
        sqlcommand = "INSERT INTO server_playlists(guildid, playlist) VALUES (%s, %s)"
        vals = (guild.id, str(playlist))
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
        return
    if result:
        sqlcommand = "UPDATE server_playlists SET playlist = %s WHERE guildid = %s"
        vals = (str(playlist), guild.id)
        mycursor.execute(sqlcommand, vals)
        mydb.commit()
        return


def get_serverplaylist(guild: Guild):
    sqlcommand = "SELECT playlist FROM server_playlists WHERE guildid = %s"
    vals = (guild.id,)
    mycursor.execute(sqlcommand, vals)
    result = mycursor.fetchall()
    return result[0][0]


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


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node("[HOST]", [PORT], '[PASS]', 'eu', 'music-node')
        # self.bot.music.add_node("localhost", 7000, 'server-utils', 'eu', 'music-node')
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
            return
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
                if arg == "server-playlist":
                    playlist = get_serverplaylist(ctx.guild)
                    playlistids = playlist.strip("][").split(", ")
                    for id in playlistids:
                        print(id)
                        track = lavalink.utils.decode_track(id)
                        player.add(requester=ctx.author.id, track=track)
                    await ctx.send(f"Playlist loaded")
                    if self.check_vc.is_running():
                        self.check_vc.restart(ctx.guild, vc)
                    else:
                        self.check_vc.start(ctx.guild, vc)
                    if not player.is_playing:
                        await player.play()
                    return
                searching_message: discord.Message = await ctx.send(f"Searching for {arg}...")
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

                await searching_message.delete()
                await ctx.channel.send(embed=embed)

                def check(m):
                    return m.author.id == ctx.author.id

                reponse = await self.bot.wait_for('message', check=check)
                track = tracks[int(reponse.content) - 1]

                player.add(requester=ctx.author.id, track=track)
                if not player.is_playing:
                    await player.play()
                    # await ctx.send(f"Started playing `{track['info']['title']}`")
                    if self.check_vc.is_running():
                        self.check_vc.restart(ctx.guild, vc)
                    else:
                        self.check_vc.start(ctx.guild, vc)
                    return
                await ctx.send(f"Track `{track['info']['title']}` added to the queue")
            except Exception as error:
                print(error)
            return

        if opt == "stop":
            try:
                global in_shuffle
                global in_repeat
                player = self.bot.music.player_manager.get(ctx.guild.id)
                if player.is_playing:
                    await player.stop()
                    player.queue.clear()
                    if ctx.guild.id in in_shuffle:
                        in_shuffle[ctx.guild.id] = False
                    if ctx.guild.id in in_repeat:
                        in_repeat[ctx.guild.id] = False
            except Exception as error:
                print(error)
            return

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
            return

        if opt == "pause":
            try:
                player = self.bot.music.player_manager.get(ctx.guild.id)
                await player.set_pause(True)
                await ctx.send(f"Music paused!")
            except Exception as error:
                print(error)
            return

        if opt == "resume":
            try:
                player = self.bot.music.player_manager.get(ctx.guild.id)
                await player.set_pause(False)
                await ctx.send(f"Music resumed")
            except Exception as error:
                print(error)
            return

        if opt == "leave":
            player = self.bot.music.player_manager.get(ctx.guild.id)
            if player.is_playing:
                await player.stop()
            await self.connect_to(ctx.guild.id, None)
            return

        if opt == "skip":
            player = self.bot.music.player_manager.get(ctx.guild.id)
            await player.skip()
            await ctx.send(f"Track skipped")
            return

        if opt == "queue":
            global current_track
            player = self.bot.music.player_manager.get(ctx.guild.id)
            if not player.queue:
                await ctx.send(f"Queue is empty")
                return
            embed = discord.Embed(title="Queue",
                                  description=f"-----------------------------\nCurrently playing:\n{current_track[ctx.guild.id].title}\n-----------------------------",
                                  color=discord.Colour.darker_grey())
            i = 0
            for track in player.queue:
                i = i + 1
                embed.description = f"{embed.description}\n{i}) {track.title}"
            await ctx.send(embed=embed)
            return
        if opt == "shuffle":
            player = self.bot.music.player_manager.get(ctx.guild.id)
            if not player.is_playing or not player.queue:
                return await ctx.send(f"I'm not playing anything that can be shuffled")
            if ctx.guild.id not in in_shuffle:
                in_shuffle[ctx.guild.id] = True
                player.set_shuffle(True)
                return await ctx.send(f"Now shuffling through the queue")
            if in_shuffle[ctx.guild.id]:
                in_shuffle[ctx.guild.id] = False
                player.set_shuffle(False)
                return await ctx.send(f"Stopped shuffling through the queue")
            if not in_shuffle[ctx.guild.id]:
                in_shuffle[ctx.guild.id] = True
                player.set_shuffle(True)
                return await ctx.send(f"Now shuffling through the queue")
            return
        if opt == "repeat":
            player = self.bot.music.player_manager.get(ctx.guild.id)
            if not player.is_playing or not player.queue:
                return await ctx.send(f"I'm not playing anything that can be repeated")
            if ctx.guild.id not in in_repeat:
                in_repeat[ctx.guild.id] = True
                player.set_repeat(True)
                return await ctx.send(f"Now repeating the queue")
            if in_repeat[ctx.guild.id]:
                in_repeat[ctx.guild.id] = False
                player.set_repeat(False)
                return await ctx.send(f"Stopped repeating the queue")
            if not in_repeat[ctx.guild.id]:
                in_repeat[ctx.guild.id] = True
                player.set_repeat(True)
                return await ctx.send(f"Now repeating the queue")
            return

        if opt == "lyrics" and arg:
            global genius
            player = self.bot.music.player_manager.get(ctx.guild.id)
            # track = current_track[ctx.guild.id]
            msg: Message = await ctx.send(f"Getting the lyrics. Please be patient as this may take a while...")
            # song = get_song(arg)
            # print(f"song lyrics: {song.lyrics}")
            # if len(song.lyrics) > 4096:
            #     return await ctx.send(f"Lyrics too long to be displayed in discord. ;(")
            # elif len(song.lyrics) > 2048:
            #     lyricsembed1 = discord.Embed(title=f"Lyrics from {song.title} by {song.artist}", description=song.lyrics[:2048])
            #     lyricsembed2 = discord.Embed(title=f"", description=song.lyrics[2049:])
            #     await ctx.send(embed=lyricsembed1)
            #     await ctx.send(embed=lyricsembed2)
            #     return
            # elif len(song.lyrics) < 2018:
            #     lyricsembed = discord.Embed(title=f"Lyrics from {song.title} from {song.artist}", description=song.lyrics)
            #     await ctx.send(embed=lyricsembed)
            #     return
            music = get_song(arg)
            await msg.delete()
            if music is None:
                return await ctx.send(
                    f"No lyrics found for `{arg}`. If you believe this is an error try to search again.")
            CHARACTER_LIMIT = 2048
            i = 0
            for m in re.finditer(r'.{,%s}(?:\n|$)' % CHARACTER_LIMIT, music["lyrics"], re.DOTALL):
                if i == 0:
                    lyricsembed = discord.Embed(title=f'Lyrics from {music["name"]} by {music["artist"]}',
                                                description=m.group(0))
                    i = i + 1
                else:
                    lyricsembed = discord.Embed(title="", description=m.group(0))
                    i = i + 1

                await ctx.send(embed=lyricsembed)
            await ctx.channel.purge(limit=1)

            # lyricsembed = discord.Embed(title=f"Lyrics from {song.title} from {song.artist}", description=song.lyrics)
            # await msg.delete()
            # await ctx.send(embed=lyricsembed)
            return

        if opt == "set-playlist":
            admin_role_id = get_adminrole(ctx)
            if ctx.author not in ctx.guild.get_role(admin_role_id).members:
                await ctx.send("You are not an admin!")
                return
            player = self.bot.music.player_manager.get(ctx.guild.id)
            playlist = []
            if player.queue:
                for track in player.queue:
                    trackid = track.track
                    playlist.append(trackid)
            if current_track:
                playlist.append(current_track[ctx.guild.id].track)

            set_serverplaylist(ctx.guild, playlist)
            return await ctx.send(f"Server playlist saved. Load it using `music play server-playlist`.")
        else:
            return await ctx.send(f"Subcommand unknown or not enough arguments given.")

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
            guild_id = int(event.player.guild_id)
            channelid: int = get_idmusicchannel(guild_id)
            guild: Guild = discord.utils.get(self.bot.guilds, id=guild_id)
            channel: TextChannel = discord.utils.get(guild.text_channels, id=channelid)
            global in_repeat
            global in_shuffle
            if guild_id in in_shuffle:
                in_shuffle[guild_id] = False
            if guild_id in in_repeat:
                in_repeat[guild_id] = False
            await channel.send(f"Player disconnected because queue ended")

        if isinstance(event, lavalink.events.TrackStartEvent):
            guild_id = int(event.player.guild_id)
            channelid: int = get_idmusicchannel(guild_id)
            guild: Guild = discord.utils.get(self.bot.guilds, id=guild_id)
            channel: TextChannel = discord.utils.get(guild.text_channels, id=channelid)
            track = event.track
            # await asyncio.sleep(2)
            await channel.send(f"Now playing `{track.title}`")
            global current_track
            if guild_id in current_track:
                current_track.pop(guild_id)
            current_track[guild_id] = track

    async def connect_to(self, guild_id: int, channel_id: int):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
        global in_shuffle
        global in_repeat
        if guild_id in in_shuffle:
            in_shuffle[guild_id] = False
        if guild_id in in_repeat:
            in_repeat[guild_id] = False

    @loop(count=None)
    async def check_vc(self, guild: Guild, channel: VoiceChannel):
        member_count = len(channel.members)
        if member_count == 1:
            try:
                global in_shuffle
                global in_repeat
                player = self.bot.music.player_manager.get(guild.id)
                if player.is_playing:
                    await player.stop()
                    player.queue.clear()
                    if guild.id in in_shuffle:
                        in_shuffle[guild.id] = False
                    if guild.id in in_repeat:
                        in_repeat[guild.id] = False

                await self.connect_to(guild.id, None)
                musicchannelid: TextChannel = get_musicchannel(guild)
                actualchannel = discord.utils.get(guild.text_channels, id=musicchannelid)
                await actualchannel.send(f"Player disconnected because channel became empty")
                return self.check_vc.stop()

                self.check_vc.stop()

            except Exception as error:
                print(error)
            return
        else:
            await asyncio.sleep(30)


def setup(bot):
    # connect_mysql()
    keep_mysql.start()
    genius()
    bot.add_cog(Music(bot))
    atexit.register(exiting)
