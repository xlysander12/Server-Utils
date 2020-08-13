# Server-Utils
A discord bot with intent to get bigger


# Functions
- Custom prefix for each server
- Collective admin role (give a certain role [customizable] to every person you want to have admin rights in the bot's eyes)
- Logs system (kicks, bans and other features are reported to the logs channel [customizable])
- Global announcements (These are made by the bot's staff steam. It is a message that is sent to every server the bot is in [this feature can be disabled by the user]. This message can contain updates and other stuff we might think that is relevant [These announcements are sent to the logs chahnel])


# Commands
- Admin commands (add a suggestion if you want more):
  - announcements [yes / no]:
    - Enables or disables the global announcements feature in your server.
    
    
  - ban [member] [reason]:
    - Bans the mentioned member. This ban is registered in the logs channel and a pm is sent to the target by the bot informing that was banned.
    
    
  - changeadminrole [role]:
    - Changes the role that has admin permissions in the bot's eyes.
    
    
  - changelogschannel [channel]
    - Changes the channel to where all the logs and global announcements go to.
    
    
  - changeprefix [prefix]
    - Changes the bot's command prefix for that server.
    
    
  - clear [ammount]
    - Clears the ammount of messages given in the channel the command was executed in.
  
  
  - create-channel [name] [category]:
    - Creates a text channel (for now voice channels aren't available) with the specified name and in the specified category [if category doesn't exist, it creates it]).
    
    
  - kick [member] [reason]
    - Kicks the mentioned member. This kick is registered in the logs channel and a pm in sent to the target by the bot informing that was kicked with a new invite to join back if he wants.
    
    
  - setup
    - The perfect command to use when the bot is invited to a new server. This command allows you to configure prefix, admin role, logs channel and if you want global announcements in your server.
    
- User commands (Add a suggestion if you want more):
  - random [a] [b]:
    - Retrieves a random number between a and b.
  - roll-dice [number of dice] [number of faces]:
    - Retrieves the output of what it would be to roll specified number of dice with specified ammount of faces each.
    
- Music commands (can be executed by everyone):
  - music join:
    - Makes the bot join the channel where the member that executed the channel is connected to (for now this command is obrigatory before start playing a music).
  - music play [music]:
    - Searches the music specified, then the bot returns with a list of the 10 first results of that term in youtube. You can select which one you want by simply writing the respective number (for now, music join must be executed before start playing a music).
  - music stop:
    - Stops the current music.
    
# Conclusion
If you find any bug or want to add a suggestion feel free to open an issue.\
This is a open-source bot so you can do whatever you want with the code as long as you give needed credit and don't use it for lucrative ends.\
Feel free to add pull requests if you got a good feature working
