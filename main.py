"""My EniBot main script. Handles commands however won't store them (with exception of help)"""
from time import gmtime, strftime
import discord
import Credentials
from Commands import COMMANDS

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


def _help_response(message, user_command):
    response = 'Help displayed in the following format:\n"Command": Help_for_command\n'
    for command in COMMANDS:
        response += '\n"' + command['start'] + '": ' + command['help']
    return CLIENT.send_message(message.channel, response)

async def _command_handler(message, user_command):
    for command in COMMANDS:
        if user_command.lower().split(' ')[0] == command['start']:
            return command['func'](CLIENT, message, user_command)
    else:
        return CLIENT.send_message(message.channel, 'Unknown command. Use "help" to get a list of commands.')


@CLIENT.event
async def on_ready():
    """When the bot logs in to discord"""
    for member in CLIENT.get_all_members():
        if str(member) == LOG_USER['name']:
            LOG_USER['member'] = member
    await _log('Bot logged in with name: "' + CLIENT.user.name + '" and id: ' + CLIENT.user.id + '\n', True)

@CLIENT.event
async def on_message(message):
    """Handles any user commands"""
    prefix = '<@' + CLIENT.user.id + '> '
    if str(message.channel) == 'bot_testing' and not message.author.bot and message.content.startswith(prefix):
        user_command = message.content.replace(prefix, '', 1)
        await _log(str(message.author) + ' ran: "' + user_command + '" in server: ' + message.server.name)
        if user_command.lower().split(' ')[0] == 'help':
            await _help_response(message, user_command)
        else:
            await _command_handler(message, user_command)

CLIENT.run(Credentials.TOKEN)
