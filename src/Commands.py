"""My EniBot command list. If you have an idea for a command, get in touch!"""
import re
import random
from src.CommandSystem import CommandSystem
from src.CommandSystems.GOL import GOL_COMMANDS
from src.CommandSystems.Minecraft import MINECRAFT_COMMANDS

COMMANDS = CommandSystem()


COMMANDS.add_command_system(
    'gol',
    cmd_help='Game of life genetic algorithm commands.',
    cmd_system=GOL_COMMANDS
)


COMMANDS.add_command_system(
    'minecraft',
    cmd_help='Commands todo with minecraft.',
    cmd_system=MINECRAFT_COMMANDS
)


async def _list_users(client, user_command, message):
    output = 'User list:'
    for server in client.servers:
        output += '\n`' + str(server) + '`:'
        for member in server.members:
            output += ' `' + str(member) + '`,'
        output = output[:-1] + '\n'
    await client.send_message(message.channel, output[:-1])

def _check_owner(client, user_command, message):
    if str(message.author) == 'eniallator#4937':
        return True

COMMANDS.add_command(
    'list_users',
    cmd_func=_list_users,
    cmd_help='Lists all users that this bot can see.',
    check_perms=_check_owner
)


async def _ping(client, user_command, message):
    await client.send_message(message.channel, 'Pong!')

COMMANDS.add_command(
    'ping',
    cmd_func=_ping,
    cmd_help='Replies with "Pong!"'
)


async def _ran_user(client, user_command, message):
    print(list(message.server.members))
    user = random.choice(list(message.server.members))
    await client.send_message(message.channel, 'I choose <@' + user.id + '>')

COMMANDS.add_command(
    'ran_user',
    cmd_func=_ran_user,
    cmd_help='Picks a random user within the server.',
    check_perms=lambda client, user_command, message: message.server
)


async def _source_code(client, user_command, message):
    await client.send_message(message.channel, 'https://github.com/eniallator/Discord-EniBot')

COMMANDS.add_command(
    'source_code',
    cmd_func=_source_code,
    cmd_help='Replies with the source code link.'
)


NUMBER_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
EMOJI_TRANSLATIONS = {
    r'[\s]': lambda char, _: {'out': ':white_large_square: '},
    r'[a-zA-Z]': lambda char, _: {'out': ':regional_indicator_' + char.lower() + ': '},
    r'[0-9]': lambda char, _: {'out': ':' + NUMBER_WORDS[int(char)] + ': '},
    r'[?]': lambda char, _: {'out': ':question: '},
    r'[!]': lambda char, _: {'out': ':exclamation: '},
    r'<@[0-9]*>': lambda user_id, message: {'inp': _find_mention(user_id, message)}
}


def _find_mention(user_id, message):
    for member in message.mentions:
        if user_id[2:-1] == member.id:
            return re.sub(r'#\d*$', '', str(member))
    return ''

async def _emojify(client, user_command, message):
    emoji_text = ''
    input_text = ' '.join(user_command.split(' ')[1:])
    while input_text:
        max_val = ''
        max_regex_key = ''
        for regex in EMOJI_TRANSLATIONS:
            curr_val = re.match('^' + regex, input_text)
            if curr_val and len(curr_val.group(0)) > len(max_val):
                max_val = curr_val.group(0)
                max_regex_key = regex
        if max_regex_key:
            input_text = input_text[len(max_val) or 1:]
            translated_output = EMOJI_TRANSLATIONS[max_regex_key](max_val, message)
            if 'out' in translated_output:
                emoji_text += translated_output['out']
            if 'inp' in translated_output:
                input_text = translated_output['inp'] + input_text
        else:
            input_text = input_text[1:]
    if emoji_text:
        await client.send_message(message.channel, emoji_text)
        return
    await client.send_message(message.channel, 'Bad input. Can only handle characters that ' + ''.join(EMOJI_TRANSLATIONS.keys()) + ' picks up.')

COMMANDS.add_command(
    'emojify',
    cmd_func=_emojify,
    cmd_help='Generates emojis from the input text'
)


CONSECUTIVE_CASE_LIMIT = 2

async def _ran_case(client, user_command, message):
    input_text = ' '.join(user_command.split(' ')[1:])
    past_cases = []
    output = ''
    for char in input_text:
        case = random.randint(0, 1)
        if sum(past_cases) == CONSECUTIVE_CASE_LIMIT:
            case = 0
        elif not sum(past_cases):
            case = 1
        past_cases = [case] + past_cases
        while len(past_cases) > CONSECUTIVE_CASE_LIMIT:
            del past_cases[len(past_cases) - 1]
        output += char.upper() if case else char.lower()
    await client.send_message(message.channel, output)

COMMANDS.add_command(
    'ran_case',
    cmd_func=_ran_case,
    cmd_help='Makes inputted text into it\'s random capitals equivalent like this: tEXt liKE This'
)


async def _spaces(client, user_command, message):
    input_text = ' '.join(user_command.split(' ')[1:])
    spaces_list = list(re.sub(r'\s*', '', input_text))
    output = ' '.join(spaces_list) or 'No input given. This command needs text input.'
    await client.send_message(message.channel, output)

COMMANDS.add_command(
    'spaces',
    cmd_func=_spaces,
    cmd_help='Removes existing spaces and puts 1 space in between each character'
)
