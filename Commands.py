"""My EniBot command list. If you have an idea for a command, get in touch!"""
import re
import random
from GOL_Sim.GOL_Simulation import GOL_Simulation
from CommandSystem import CommandSystem

COMMANDS = CommandSystem()


async def _ping(client, user_command, message, iteration):
    return {'output': 'Pong!'}

COMMANDS.add_command(
    'ping',
    cmd_func=_ping,
    cmd_help=lambda client, user_cmd, message: 'Replies with "Pong!"'
)


async def _source_code(client, user_command, message, iteration):
    return {'output': 'https://github.com/eniallator/Discord-EniBot'}

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

async def _emojify(client, user_command, message, iteration):
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
    if not emoji_text:
        emoji_text = 'Bad input. Can only handle characters that ' + ''.join(EMOJI_TRANSLATIONS.keys()) + ' picks up.'
    return {'output': emoji_text}

COMMANDS.add_command(
    'emojify',
    cmd_func=_emojify,
    cmd_help=lambda client, user_cmd, message: 'Generates emojis from the input text'
)


async def _ran_case(client, user_command, message, iteration):
    input_text = ' '.join(user_command.split(' ')[1:])
    ran_case_list = [random.choice([char.lower(), char.upper()]) for char in input_text]
    return {'output': ''.join(ran_case_list)}

COMMANDS.add_command(
    'ran_case',
    cmd_func=_ran_case,
    cmd_help=lambda client, user_cmd, message: 'Makes inputted text into it\'s random capitals equivalent like this: tEXt liKE This'
)


async def _spaces(client, user_command, message, iteration):
    input_text = ' '.join(user_command.split(' ')[1:])
    spaces_list = list(re.sub('\s*', '', input_text))
    return {'output': ' '.join(spaces_list)}

COMMANDS.add_command(
    'spaces',
    cmd_func=_spaces,
    cmd_help=lambda client, user_cmd, message: 'Removes existing spaces and puts 1 space in between each character'
)


COMMANDS.add_command_system(
    'gol',
    cmd_help=lambda client, user_cmd, message: 'Game of life genetic algorithm commands.'
)
GOL_INSTANCES = {}
GOL_MAX_PROCESSING = 50 ** 50 * (7 * 7)
GOL_MAX_CYCLES = 25


def _numberify(terms):
    num_terms = []
    for index, term in enumerate(terms):
        try:
            if '.' in term:
                num_terms.append(float(term))
            else:
                num_terms.append(int(term))
        except ValueError:
            return index
    return num_terms

def _gol_new_validate(args):
    default_vals = [50, 5, 5, 30]
    intensive_args = [args[i] if len(args) > i else val for i, val in enumerate(default_vals)]
    accumulator = intensive_args[0] ** intensive_args[3] * (intensive_args[1] * intensive_args[2])
    if accumulator <= GOL_MAX_PROCESSING:
        return True

async def _gol_new(client, command_terms, message, iteration):
    string_args = command_terms[1:]
    args = _numberify(string_args)
    response = ''
    
    if not message.server:
        response = 'GOL commands will only work on a server.'
    elif isinstance(args, int):
        response += 'The term at index ' + str(args + 2) + ' has to be a number.\n'
    elif len(args) > 6:
        response += 'Expecting 6 or less terms.'
    
    if not response and str(message.server):
        if _gol_new_validate(args):
            if str(message.server) in GOL_INSTANCES:
                del GOL_INSTANCES[str(message.server)]
            try:
                GOL_INSTANCES[str(message.server)] = GOL_Simulation(*args)
                response = 'Successfully created a new game of life genetic algorithm.'
            except:
                response = 'All arguments have to be integers except for mutation chance which is a float.'
        else:
            response = 'Max processing exceeded. Please choose smaller input arguments.'
    
    return {'output': response}

COMMANDS.add_command(
    ['gol', 'new'],
    cmd_func=_gol_new,
    cmd_help=lambda client, user_cmd, message: 'Create a new game of life genetic algorithm.',
    specific_help=lambda client, user_cmd, message: 'Where all arguments are optional and all are numbers.\nDefaults: `size=50, width=5, height=5, iterations=30, mutation_chance=0.025, creatures_to_remain=5`\nUsage: `gol new size width height iterations mutation_chance creatures_to_remain`'
)


def _validate_gol_instance(server):
    if server and server in GOL_INSTANCES:
        return ''
    else:
        return 'Game of life instance does not exist. To create, use `gol new`'

def _cycle_instance(instance):
    instance.evaluate()
    response = instance.stats()
    instance.evolve_population()
    return response

async def _gol_next_cycle(client, command_terms, message, iteration):
    response = _validate_gol_instance(str(message.server))
    if not response:
        response = _cycle_instance(GOL_INSTANCES[str(message.server)])
    return {'output': response}

COMMANDS.add_command(
    ['gol', 'next_cycle'],
    cmd_func=_gol_next_cycle,
    cmd_help=lambda client, user_cmd, message: 'Evolves the population and gives stats for the population.',
    specific_help=lambda client, user_cmd, message: 'Receives no arguments.\nFirst it will evaluate and then it will get the stats after evaluation and finally evolve the population.'
)


async def _gol_cycle(client, command_terms, message, iteration):
    response = {}
    output_message = _validate_gol_instance(str(message.server))
    if not output_message:
        try:
            response['limit'] = int(command_terms[1])
            if 1 <= response['limit'] <= GOL_MAX_CYCLES:
                output = _cycle_instance(GOL_INSTANCES[str(message.server)])
                if iteration + 1 >= response['limit']:
                    output_message = output
            else:
                output_message = 'Limit out of range. Choose an integer between 1-' + str(GOL_MAX_CYCLES) + '.'
        except ValueError:
            output_message = 'The second argument has to be an integer between 1-' + str(GOL_MAX_CYCLES) + '.'
    if output_message:
        response['output'] = output_message
    return response

COMMANDS.add_command(
    ['gol', 'cycle'],
    cmd_func=_gol_cycle,
    cmd_help=lambda client, user_cmd, message: 'Evolves the population a number of times and gives stats for the population afterwards.',
    specific_help=lambda client, user_cmd, message: 'Receives 1 argument; a number from 1-' + str(GOL_MAX_CYCLES) + ' to cycle through the simulation.\n Usage: `gol cycle limit`'
)
