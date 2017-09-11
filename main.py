import asyncio
import discord

from time import gmtime, strftime

import Credentials
from Commands import COMMANDS

CLIENT = discord.Client()

def _get_time():
    raw_time = strftime("%Y/%m/%d %H:%M:%S", gmtime())
    return '[' + raw_time + '] '

def _log(msg_to_log):
    print(_get_time() + msg_to_log)
    # Might do some file I/O stuff here

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
        user_command = message.content.replace(prefix, '', 1)
        if user_command.lower().split(' ')[0] == 'help':
            _log(str(message.author) + ' ran: "' + user_command + '" in server: ' + message.server.name)
            response = 'Help displayed in the following format:\n"Command": Help_for_command\n'
            for command in COMMANDS:
                response += '\n"' + command['start'] + '": ' + command['help']

            await CLIENT.send_message(message.channel, response)
        else:
            for command in COMMANDS:
                if user_command.lower().split(' ')[0] == command['start']:
                    _log(str(message.author) + ' ran: "' + user_command + '" in server: ' + message.server.name)
                    await command['func'](CLIENT, message, user_command)
                    break
            else:
                _log(str(message.author) + ' tried to run: "' + user_command + '" in server: ' + message.server.name)
                await CLIENT.send_message(message.channel, 'Unknown command. Use "help" to get a list of commands.')

CLIENT.run(Credentials.TOKEN)
