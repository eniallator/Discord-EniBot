"""My EniBot command list. If you have an idea for a command, get in touch!"""
import re
import random
from src.CommandSystem import CommandSystem
from src.CommandSystems.GOL import GOL_COMMANDS

COMMANDS = CommandSystem()

COMMANDS.add_command_system(
    'gol',
    cmd_help=lambda client, user_cmd, message: 'Game of life genetic algorithm commands.',
    cmd_system=GOL_COMMANDS
)

async def _ping(client, user_command, message):
    return 'Pong!'

COMMANDS.add_command(
    'ping',
    cmd_func=_ping,
    cmd_help=lambda client, user_cmd, message: 'Replies with "Pong!"'
)


async def _source_code(client, user_command, message):
    return 'https://github.com/eniallator/Discord-EniBot'

COMMANDS.add_command(
    'source_code',
    cmd_func=_source_code,
    cmd_help=lambda client, user_cmd, message: 'Replies with the source code link.'
)


NUMBER_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
EMOJI_TRANSLATIONS = {
    '[\s]': lambda char, _: {'out': ':white_large_square: '},
    '[a-zA-Z]': lambda char, _: {'out': ':regional_indicator_' + char.lower() + ': '},
    '[0-9]': lambda char, _: {'out': ':' + NUMBER_WORDS[int(char)] + ': '},
    '[?]': lambda char, _: {'out': ':question: '},
    '[!]': lambda char, _: {'out': ':exclamation: '},
    '<@[0-9]*>': lambda user_id, message: {'inp': _find_mention(user_id, message)}
}


def _find_mention(user_id, message):
    print(user_id, [m.id for m in message.mentions])
    for member in message.mentions:
        if user_id[2:-1] == member.id:
            return re.sub('#\d*$', '', str(member))
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
            input_text = input_text[len(max_val) if max_val else 1:]
            translated_output = EMOJI_TRANSLATIONS[max_regex_key](max_val, message)
            if 'out' in translated_output:
                emoji_text += translated_output['out']
            if 'inp' in translated_output:
                input_text = translated_output['inp'] + input_text
        else:
            input_text = input_text[1:]
    if emoji_text:
        return emoji_text
    return 'Bad input. Can only handle characters that ' + ''.join(EMOJI_TRANSLATIONS.keys()) + ' picks up.'

COMMANDS.add_command(
    'emojify',
    cmd_func=_emojify,
    cmd_help=lambda client, user_cmd, message: 'Generates emojis from the input text'
)


async def _ran_case(client, user_command, message):
    input_text = ' '.join(user_command.split(' ')[1:])
    ran_case_list = [random.choice([char.lower(), char.upper()]) for char in input_text]
    return ''.join(ran_case_list)

COMMANDS.add_command(
    'ran_case',
    cmd_func=_ran_case,
    cmd_help=lambda client, user_cmd, message: 'Makes inputted text into it\'s random capitals equivalent like this: tEXt liKE This'
)


async def _spaces(client, user_command, message):
    input_text = ' '.join(user_command.split(' ')[1:])
    spaces_list = list(re.sub('\s*', '', input_text))
    return ' '.join(spaces_list)

COMMANDS.add_command(
    'spaces',
    cmd_func=_spaces,
    cmd_help=lambda client, user_cmd, message: 'Removes existing spaces and puts 1 space in between each character'
)
