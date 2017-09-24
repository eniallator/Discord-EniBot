"""My EniBot command list. If you have an idea for a command, get in touch!"""
from GOL_Sim.GOL_Simulation import GOL_Simulation
import re

COMMANDS = []


def _ping(client, message, user_command, iteration):
    return {'output': 'Pong!'}

COMMANDS.append({
    'start': 'ping',
    'help': 'Replies with "Pong!"',
    'func': _ping
})


def _source_code(client, message, user_command, iteration):
    return {'output': 'https://github.com/eniallator/Discord-EniBot'}

COMMANDS.append({
    'start': 'source_code',
    'help': 'Replies with the source code link.',
    'func': _source_code
})


NUMBER_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
EMOJI_TRANSLATIONS = {
    '\s': lambda char: ':white_large_square: ',
    'a-zA-Z': lambda char: ':regional_indicator_' + char.lower() + ': ',
    '0-9': lambda char: ':' + NUMBER_WORDS[int(char)] + ': ',
    '?': lambda char: ':question: ',
    '!': lambda char: ':exclamation: '
}


def _emojify(client, message, user_command, iteration):
    emoji_text = ''
    input_text = ' '.join(user_command.split(' ')[1:])
    regex_all = '[' + ''.join(EMOJI_TRANSLATIONS.keys()) + ']'
    for match in re.finditer(regex_all, input_text):
        char = match.group(0)
        for regex in EMOJI_TRANSLATIONS:
            if re.match('[' + regex + ']', char):
                emoji_text += EMOJI_TRANSLATIONS[regex](char)
                break
    if not emoji_text:
        emoji_text = 'Bad input. Can only handle characters that ' + regex_all + ' picks up.'
    return {'output': emoji_text}

COMMANDS.append({
    'start': 'emojify',
    'help': 'Generates emojis from the input text based on the following regex: [' + ''.join(EMOJI_TRANSLATIONS.keys()) + ']',
    'func': _emojify
})


GOL_COMMANDS = []
GOL_INSTANCES = {}
GOL_MAX_PROCESSING = 75 ** 50 * (10 * 10)
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
    accumulator = intensive_args[0] ** intensive_args[1] * (intensive_args[1] * intensive_args[2])
    if accumulator <= GOL_MAX_PROCESSING:
        return True

def _gol_new(client, message, command_terms, iteration):
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

GOL_COMMANDS.append({
    'start': 'new',
    'help': 'Create a new game of life genetic algorithm.',
    'specific_help': 'Where all arguments are optional and all are numbers.\nDefaults: `size=50, width=5, height=5, iterations=30, mutation_chance=0.025, creatures_to_remain=5`\nUsage: `gol new size width height iterations mutation_chance creatures_to_remain`',
    'func': _gol_new
})


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

def _gol_next_cycle(client, message, command_terms, iteration):
    response = _validate_gol_instance(str(message.server))
    if not response:
        response = _cycle_instance(GOL_INSTANCES[str(message.server)])
    return {'output': response}

GOL_COMMANDS.append({
    'start': 'next_cycle',
    'help': 'Evolves the population and gives stats for the population.',
    'specific_help': 'Receives no arguments.\nFirst it will evaluate and then it will get the stats after evaluation and finally evolve the population.',
    'func': _gol_next_cycle
})


def _gol_cycle(client, message, command_terms, iteration):
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

GOL_COMMANDS.append({
    'start': 'cycle',
    'help': 'Evolves the population a number of times and gives stats for the population afterwards.',
    'specific_help': 'Receives 1 argument; a number from 1-' + str(GOL_MAX_CYCLES) + ' to cycle through the simulation.\n Usage: `gol cycle limit`',
    'func': _gol_cycle
})


def _gol_help_handler(client, message, command_terms):
    response = ''
    if len(command_terms) == 1:
        response = 'gol help displayed in the following format:\n"gol Command": Help_for_command\n'
        for command in GOL_COMMANDS:
            response += '\n"' + command['start'] + '": ' + command['help']
        response += '\n\nUse `gol help COMMAND` to get more help on specific commands.'
    else:
        for command in GOL_COMMANDS:
            if len(command_terms) > 1 and command['start'] == command_terms[1]:
                response = command['specific_help']
                break
        else:
            response = 'Unknown game of life help command. Use "gol help" to get a list of commands.'
    return {'output': response}

def _gol(client, message, user_command, iteration):
    command_terms = user_command.split(' ')[1:]
    if not len(command_terms) or command_terms[0] == 'help':
        return _gol_help_handler(client, message, command_terms)
    else:
        for command in GOL_COMMANDS:
            if command['start'] == command_terms[0].lower():
                return command['func'](client, message, command_terms, iteration)

COMMANDS.append({
    'start': 'gol',
    'help': 'Game of life genetic algorithm commands.',
    'func': _gol
})