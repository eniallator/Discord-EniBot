"""My EniBot main script"""
import sys
import os
from time import gmtime, strftime
import discord
from src.Commands import COMMANDS

TOKEN = os.environ.get('DISCORD_TOKEN')

if not TOKEN:
    try:
        from Credentials import TOKEN
    except ModuleNotFoundError:
        if len(sys.argv) > 1:
            TOKEN = sys.argv[1]
        else:
            raise Exception('Specify discord token either with a credentials.py file or as an argument.')

CLIENT = discord.Client()

LOG_USER = {}
LOG_USER['name'] = 'eniallator#4937'

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

@CLIENT.event
async def on_message(message):
    """Handles any user commands"""
    prefix = '<@' + CLIENT.user.id + '> '
    user_command = ''
    if message.content.startswith(prefix):
        user_command = message.content.replace(prefix, '', 1)
    elif not message.server:
        user_command = message.content

    if not message.author.bot and user_command:
        user_command = message.content.replace(prefix, '', 1)
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
            help_message = COMMANDS.get_help(CLIENT, help_command, message)
            await CLIENT.send_message(message.channel, help_message)
        else:
            response = await COMMANDS.execute(user_command, CLIENT, user_command, message)
            await CLIENT.send_message(message.channel, response)

CLIENT.run(TOKEN)
