# Server-Utils
A discord bot with intent to have as many features as possible in order to decrease the ammount of bots needed in a server


# Features
- Custom prefix for each server
- Collective admin role (give a certain role [customizable] to every person you want to have admin rights in the bot's eyes)
- Logs system (kicks, bans and other features are reported to the logs channel [customizable])
- Global announcements (These are made by the bot's staff steam. It is a message that is sent to every server the bot is in [this feature can be disabled by the user]. This message can contain updates and other stuff we might think that is relevant [These announcements are sent to the logs channel])
- Ticket system (An easy way for members to ask for support)
- Customizable messages for when a person joins or leaves the server.
- Spicy content (Because, why not?)
- Invites counting and inviter leaderboard


# Commands
- Admin commands (add a suggestion if you want more):
  - announcements [yes / no]:
    - Enables or disables the global announcements feature in your server.
  - autorole:
    - Enables or disables the automatic role feature.
  - ban [member] [reason]:
    - Bans the mentioned member. This ban is registered in the logs channel and a pm is sent to the target by the bot informing that was banned.    
  - changeadminrole [role]:
    - Changes the role that can execute admin commands.
  - changelogschannel [channel]:
    - Changes the channel to where all the logs and global announcements go to.
  - changemusicchannel [channel]:
    - Changes the channel where music commands are allowed.
  - changeprefix [prefix]:
    - Changes the bot's command prefix for that server.
  - clear [ammount]:
    - Clears the ammount of messages given in the channel the command was executed in.
  - create-channel [name] [category]:
    - Creates a text channel (for now voice channels aren't available) with the specified name and in the specified category [if category doesn't exist, it creates it]).
  - kick [member] [reason]:
    - Kicks the mentioned member. This kick is registered in the logs channel and a pm in sent to the target by the bot informing that was kicked with a new invite to join back if he wants.
  - setporn:
    - Enables or disables porn commands.
  - ticket-system:
    - Enables or disables the ticket system.
  - set-joinmessage:
    - Enables or disables the join message. If being enabled you can choose in which channel the messages are sent and the message you want to send.
  - set-leavemessage:
    - Enables or disables the leave message. If being enabled you can choose in which channel the messages are sent and the message you want to send.
  - setup:
    - The perfect command to use when the bot is invited to a new server. This command allows you to configure prefix, admin role, logs channel and if you want global announcements in your server.
    
- User commands (Add a suggestion if you want more):
  - random [a] [b]:
    - Retrieves a random number between a and b.
  - roll-dice [number of dice] [number of faces]:
    - Retrieves the output of what it would be to roll specified number of dice with specified ammount of faces each.
  - color-pick [color]:
    - Randomizes one color, if user gets the color right it wins... nothing.
  - meme [type]:
    - Gets a meme of the specified type (if none default meme is sent).
  - aww:
    - Gets a cute pic
  - server:
    - Gets information about the server.
  - info [user]:
    - Gets information about the specified user.
  - invites [user]:
    - Gets the number of invites an user has. (Only counts those after the bot was added).
  - invite-leaderboard:
    - Gets the top 5 inviters of the server (Only counts invites after the bot was added).
  - help [page]:
    - Shows the help menu.
    
- Music commands (Can be executed by everyone):
  - music join:
    - Makes the bot join the channel where the member that executed the channel is connected to.
  - music play [music]/server-playlist:
    - Searches the specified music, then the bot returns with a list of the 10 first results of that term in youtube. You can select which one you want by simply writing the respective number. If server-playlist argument is given then it loads and plays the server playlist (Can be set by using music set-playlist).
  - music pause:
    - Pauses the current music playing.
  - music resume:
    - Resumes the current music if paused.
  - music stop:
    - Stops the current music.
  - music leave:
    - Makes the bot disconnect from the voice channel.
  - music skip:
    - Skips the current music and starts playing the next one in queue. If there's no next music in queue, the bot disconnects from the channel.
  - music queue:
    - Shows the current music and queue.
  - music shuffle:
    - Makes the bot randozime the next song in the queue.
  - music repeat:
    - Makes the bot repeat the whole queue until disabled.
  - music lyrics [song]:
    - Gets the lyrics of the specified song .
  - music volume:
    - Changes the volume of the music (Value of 10% is recomended to not cause hearing issues and not to lose sound quality).
  - music set-playlist:
    - Sets the current track and queue to the server playlist. This playlist can be played by using music play server-playlist.
    
- Porn commands (Can be executed by everyone if active in the server):
  - porn ass:
    - Gets a pic or gif of an ass.
  - porn balls:
    - Gets a pic or gif of some balls.
  - porn boobs:
    - Gets a pic or gif of a pair of boobs.
  - porn dick:
    - Gets a pic or gif of a dick.
  - porn gay:
    - Gets a pic or gif of a gay video.
  - porn lesbian:
    - Gets a pic or gif of a lesbian video.
  - porn pussy:
    - Gets a pic or gif of a pussy.
  - porn sex:
    - Gets a pic or gif of a porn video.
# Conclusion
If you find any bug or want to add a suggestion feel free to open an issue.\
This is a open-source bot so you can do whatever you want with the code as long as you give needed credit and don't use it for lucrative ends.\
Feel free to add pull requests if you got a good feature working
