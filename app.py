"""My EniBot main script"""
import sys
import os
import configparser
from time import gmtime, strftime
import discord
from Config import OWNER, MULTI_COMMAND_LANGUAGE
from src.Commands import COMMANDS

TOKEN = os.environ.get('DISCORD_TOKEN')

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

async def get_last_msg():
    if 'member' not in LOG_USER:
        return

    await CLIENT.start_private_message(LOG_USER['member'])
    for channel in CLIENT.private_channels:
        if len(channel.recipients) == 1 and channel.recipients[0].id == LOG_USER['member'].id:
            log_channel = channel

    async for msg in CLIENT.logs_from(log_channel, limit=1):
        return msg

async def _log(msg_to_log, first_log=False):
    timestamp_msg = _get_time() + msg_to_log
    edit_last_msg = False

    if first_log:
        last_msg = await get_last_msg()
        if last_msg and last_msg.author.id == CLIENT.user.id and last_msg.content.startswith('-'):
            edit_last_msg = True
        else:
            timestamp_msg = '-' * 90 + '\n' + timestamp_msg

    print(timestamp_msg)
    if edit_last_msg:
        await CLIENT.edit_message(last_msg, last_msg.content + '\r\n' + timestamp_msg)
    elif 'member' in LOG_USER:
        await CLIENT.send_message(LOG_USER['member'], timestamp_msg)


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
    log_routine = None
    max_cmds = 10
    if len(cmds) > max_cmds:
        await CLIENT.send_message(message.channel, 'Error: multi command handler can handle at max ' + str(max_cmds) + ' commands')
        log_routine = _log(str(message.author) + ' tried to run ' + str(len(cmds)) + ' commands within a multi-command')
        return

    log_message = str(message.author) + ' ran a multi-command containing: "' + '", "'.join(cmds) + '"'
    suffix = ' in server: "' + message.server.name + '"' if message.server else ' in a private message'
    log_routine = _log(log_message + suffix)

    if LOG_USER['name'] != str(message.author) or message.server:
        await log_routine

    for cmd in cmds:
        await command_hander(message, cmd, logging=False)

# Create a new client class that inherits the discord.Client class which can get all the send_message calls and pipe them into another command
# Or redesign and refactor the current system to make it so that each command has an output which can be piped into other commands
@CLIENT.event
async def on_message(message):
    """Handles any user commands"""
    if message.author.id == CLIENT.user.id:
        return
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
        await command_hander(message, message.content)


CLIENT.run(TOKEN)
