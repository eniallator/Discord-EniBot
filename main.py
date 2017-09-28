"""My EniBot main script. Handles commands however won't store them (with exception of help)"""
import sys
from time import gmtime, strftime
import discord
from Commands import COMMANDS

TOKEN = None

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

PROGRESS_MESSAGE = {}
PROGRESS_MESSAGE['format'] = lambda curr, limit: 'Progress: ' + str(curr / limit * 100)[:5] + '%'


async def _send_progress(message, curr, limit):
    if PROGRESS_MESSAGE['new_message']:
        PROGRESS_MESSAGE['new_message'] = False
        PROGRESS_MESSAGE['message'] = await CLIENT.send_message(message.channel, PROGRESS_MESSAGE['format'](curr, limit))
    else:
        PROGRESS_MESSAGE['message'] = await CLIENT.edit_message(PROGRESS_MESSAGE['message'], PROGRESS_MESSAGE['format'](curr, limit))


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
            response = {}
            iteration = 0
            PROGRESS_MESSAGE['new_message'] = True

            while 'output' not in response:
                response = command['func'](CLIENT, message, user_command, iteration)
                if 'output' in response:
                    await CLIENT.send_message(message.channel, response['output'])
                else:
                    await _send_progress(message, iteration + 1, response['limit'])
                iteration += 1
            
            if 'message' in PROGRESS_MESSAGE:
                await CLIENT.delete_message(PROGRESS_MESSAGE['message'])
                del PROGRESS_MESSAGE['message']
            
            return response['output']
    else:
        return await CLIENT.send_message(message.channel, 'Unknown command. Use "help" to get a list of commands.')


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
            await _help_response(message, user_command)
        else:
            await _command_handler(message, user_command)

CLIENT.run(TOKEN)
