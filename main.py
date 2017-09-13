"""My EniBot main script. Handles commands however won't store them (with exception of help)"""
from time import gmtime, strftime
import discord
import Credentials
from Commands import COMMANDS

CLIENT = discord.Client()
log_user = {}
log_user['name'] = 'eniallator#4937'

log_stack = ['------------------------------------------------------------------------------------------------\n']

def _get_time():
    raw_time = strftime("%Y/%m/%d %H:%M:%S", gmtime())
    return '[' + raw_time + '] '

def _log(msg_to_log):
    timestamp_msg = _get_time() + msg_to_log
    print(timestamp_msg)
    log_stack.append(timestamp_msg)

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
    for member in CLIENT.get_all_members():
        if str(member) == log_user['name']:
            log_user['member'] = member
    _log('Bot logged in with name: "' + CLIENT.user.name + '" and id: ' + CLIENT.user.id + '\n')

@CLIENT.event
async def on_message(message):
    """Handles any user commands"""
    prefix = '<@' + CLIENT.user.id + '> '
    if not message.channel.is_private and message.author == CLIENT.user and 'member' in log_user:
        log_user_msg = ''
        for log_msg in log_stack:
            log_user_msg += log_msg + '\n'
        del log_stack[:]
        await CLIENT.send_message(log_user['member'], log_user_msg)

    elif str(message.channel) == 'bot_testing' and not message.author.bot and message.content.startswith(prefix):
        user_command = message.content.replace(prefix, '', 1)
        if user_command.lower().split(' ')[0] == 'help':
            await _help_response(message, user_command)
        else:
            await _command_handler(message, user_command)

CLIENT.run(Credentials.TOKEN)
