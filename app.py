"""My EniBot main script"""
import sys
import os
import configparser
from time import gmtime, strftime
import discord
from Config import OWNER
from src.Commands import COMMANDS

TOKEN = os.environ.get('DISCORD_TOKEN')
MULTI_COMMAND_LANGUAGE = 'enibot'

if not TOKEN:
    try:
        config = configparser.ConfigParser()
        config.read('auth.ini')
        TOKEN = config.get('discord', 'token')
    except configparser.NoSectionError:
        if len(sys.argv) > 1:
            TOKEN = sys.argv[1]
        else:
            raise Exception('Specify discord token either with a auth.ini file or as an argument.')


CLIENT = discord.Client()


LOG_USER = {}
LOG_USER['name'] = OWNER

def _get_time():
    raw_time = strftime("%Y/%m/%d %H:%M:%S", gmtime())
    return '[' + raw_time + '] '

def _log(msg_to_log, first_log=False):
    timestamp_msg = _get_time() + msg_to_log
    if first_log:
        timestamp_msg = '-' * 90 + '\n' +timestamp_msg
    print(timestamp_msg)
    if 'member' in LOG_USER:
        return CLIENT.send_message(LOG_USER['member'], timestamp_msg)


@CLIENT.event
async def on_ready():
    """When the bot logs in to discord"""
    for member in CLIENT.get_all_members():
        if str(member) == LOG_USER['name']:
            LOG_USER['member'] = member
    await _log('Bot logged in with name: "' + CLIENT.user.name + '" and id: ' + CLIENT.user.id + '\n', first_log=True)

async def command_hander(message, user_command, logging=True):
    if logging:
        log_message = str(message.author) + ' ran: "' + user_command + '"'
        if message.server:
            log_message += ' in server: ' + message.server.name
        else:
            log_message += ' in a private message'
        log_routine = _log(log_message)
        if LOG_USER['name'] != str(message.author) or message.server:
            await log_routine

    if user_command.lower().split(' ')[0] == 'help':
        help_command = ' '.join(user_command.split(' ')[1:])
        help_message = COMMANDS.get_help(help_command, CLIENT, help_command, message)
        await CLIENT.send_message(message.channel, help_message)
    else:
        output = await COMMANDS.execute(user_command, CLIENT, user_command, message)
        if isinstance(output, str):
            await CLIENT.send_message(message.channel, output)

async def multi_command_handler(message, multi_command):
    cmds = multi_command.split('\n')
    cmds = list(filter(lambda cmd: cmd != '', cmds))
    max_cmds = 10
    if len(cmds) > max_cmds:
        await CLIENT.send_message(message.channel, 'Error: multi command handler can handle at max ' + str(max_cmds) + ' commands')
        _log(str(message.author) + ' tried to run ' + str(len(cmds)) + ' commands within a multi-command')
        return

    log_message = str(message.author) + ' ran a multi-command containing: "' + '", "'.join(cmds) + '"'
    suffix = ' in server: "' + message.server.name + '"' if message.server else ' in a private message'
    _log(log_message + suffix)
    for cmd in cmds:
        await command_hander(message, cmd, logging=False)

@CLIENT.event
async def on_message(message):
    """Handles any user commands"""
    prefix = '<@' + CLIENT.user.id + '> '
    multi_command_prefix = '```' + MULTI_COMMAND_LANGUAGE + '\n'
    multi_command_start = message.content.find(multi_command_prefix)
    if message.content.startswith(prefix):
        user_command = message.content.replace(prefix, '', 1)
        await command_hander(message, user_command)
    elif multi_command_start >= 0:
        multi_command = message.content[multi_command_start + len(multi_command_prefix):]
        multi_command = multi_command[:multi_command.find('```')]
        await multi_command_handler(message, multi_command)
    elif not message.server:
        user_command = message.content


CLIENT.run(TOKEN)
