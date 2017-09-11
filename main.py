import asyncio
import discord

from time import gmtime, strftime

import Credentials
from Commands import COMMANDS

CLIENT = discord.Client()

def _get_time():
    raw_time = strftime("%Y/%m/%d %H:%M:%S", gmtime())
    return '[' + raw_time + '] '

@CLIENT.event
async def on_ready():
    print('Logged in as')
    print(CLIENT.user.name)
    print(CLIENT.user.id)
    print('------')

@CLIENT.event
async def on_message(message):
    prefix = '<@' + CLIENT.user.id + '> '
    if str(message.channel) == 'bot_testing' and not message.author.bot and message.content.startswith(prefix):
        for command in COMMANDS:
            user_command = message.content.replace(prefix, '', 1)
            if user_command.lower().startswith(command['start']):
                print(_get_time() + str(message.author) + ' ran: "' + user_command + '" in server: ' + message.server.name)
                await command['func'](CLIENT, message, user_command)
                break

CLIENT.run(Credentials.TOKEN)
