"""My EniBot main script. Handles commands however won't store them (with exception of help)"""
from time import gmtime, strftime

# import asyncio
import discord

import Credentials
from Commands import COMMANDS

CLIENT = discord.Client()

def _get_time():
    raw_time = strftime("%Y/%m/%d %H:%M:%S", gmtime())
    return '[' + raw_time + '] '

def _log(msg_to_log):
    print(_get_time() + msg_to_log)
    # Might do some file I/O stuff here

def _help_response(message, user_command):
    _log(str(message.author) + ' ran: "' + user_command + '" in server: ' + message.server.name)
    response = 'Help displayed in the following format:\n"Command": Help_for_command\n'
    for command in COMMANDS:
        response += '\n"' + command['start'] + '": ' + command['help']
    return CLIENT.send_message(message.channel, response)

def _command_handler(message, user_command):
    for command in COMMANDS:
        if user_command.lower().split(' ')[0] == command['start']:
            _log(str(message.author) + ' ran: "' + user_command + '" in server: ' + message.server.name)
            return command['func'](CLIENT, message, user_command)
    else:
        _log(str(message.author) + ' tried to run: "' + user_command + '" in server: ' + message.server.name)
        return CLIENT.send_message(message.channel, 'Unknown command. Use "help" to get a list of commands.')

@CLIENT.event
async def on_ready():
    """When the bot logs in to discord"""
    print('Logged in as')
    print(CLIENT.user.name)
    print(CLIENT.user.id)
    print('------')

@CLIENT.event
async def on_message(message):
    """Handles any user commands"""
    prefix = '<@' + CLIENT.user.id + '> '
    if str(message.channel) == 'bot_testing' and not message.author.bot and message.content.startswith(prefix):
        user_command = message.content.replace(prefix, '', 1)
        if user_command.lower().split(' ')[0] == 'help':
            await _help_response(message, user_command)
        else:
            await _command_handler(message, user_command)

CLIENT.run(Credentials.TOKEN)
