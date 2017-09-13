"""My EniBot command list. If you have an idea for a command, get in touch!"""
from GOL_Sim.GOL_Simulation import GOL_Simulation

COMMANDS = []


def _ping(client, message, user_command):
    return client.send_message(message.channel, 'Pong!')

COMMANDS.append({
    'start': 'ping',
    'help': 'Replies with "Pong!"',
    'func': _ping
})


def _source_code(client, message, user_command):
    return client.send_message(message.channel, 'https://github.com/eniallator/Discord-EniBot')

COMMANDS.append({
    'start': 'source_code',
    'help': 'Replies with the source code link.',
    'func': _source_code
})


GOL_COMMANDS = []
GOL_INSTANCES = {}
GOL_MAX_PROCESSING = 50 ** 50 * 5 * 5
GOL_MAX_CYCLES = 10


def _gol_new(command_terms, server):
    args = command_terms[1:]
    response = ''
    for index, term in enumerate(args):
        try:
            if '.' in term:
                args[index] = float(term)
            else:
                args[index] = int(term)
        except:
            response += 'The term at index ' + str(index + 2) + ' has to be a number.\n'
    
    if len(args) > 6:
        response += 'Expecting 6 or less terms.'
    
    if not response and server:
        default_vals = [5, 5]
        accumulator = 1
        if len(args) > 0:
            accumulator *= args[0]
        else:
            accumulator *= 50
        if len(args) > 3:
            accumulator = accumulator ** args[3]
        else:
            accumulator = accumulator ** 30
        for i, val in enumerate(default_vals):
            if len(args) > i + 1:
                accumulator *= args[i + 1]
            else:
                accumulator *= val
        if accumulator <= GOL_MAX_PROCESSING:
            if server in GOL_INSTANCES:
                del GOL_INSTANCES[server]
            try:
                GOL_INSTANCES[server] = GOL_Simulation(*args)
                response = 'Successfully created a new game of life genetic algorithm.'
            except:
                response = 'All arguments have to be integers except for mutation chance which is a float.'
        else:
            response = 'Max processing exceeded. Please choose smaller input arguments.'
    elif not server:
        response = 'Instances can only be created on servers.'
    
    return response

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

def _gol_next_cycle(command_terms, server):
    response = _validate_gol_instance(server)
    if not response:
        response = _cycle_instance(GOL_INSTANCES[server])
    return response

GOL_COMMANDS.append({
    'start': 'next_cycle',
    'help': 'Evolves the population and gives stats for the population.',
    'specific_help': 'Receives no arguments.\nFirst it will evaluate and then it will get the stats after evaluation and finally evolve the population.',
    'func': _gol_next_cycle
})


def _gol_cycle(command_terms, server):
    response = _validate_gol_instance(server)
    if not response:
        try:
            limit = int(command_terms[1])
            if 1 <= limit <= GOL_MAX_CYCLES:
                for i in range(limit):
                    response = _cycle_instance(GOL_INSTANCES[server])
            else:
                response = 'Limit out of range. Choose an integer between 1-' + str(GOL_MAX_CYCLES) + '.'
        except:
            response = 'The second argument has to be an integer between 1-' + str(GOL_MAX_CYCLES) + '.'
    return response

GOL_COMMANDS.append({
    'start': 'cycle',
    'help': 'Evolves the population a number of times and gives stats for the population afterwards.',
    'specific_help': 'Receives 1 argument; a number from 1-' + str(GOL_MAX_CYCLES) + ' to cycle through the simulation.\n Usage: `gol cycle limit`',
    'func': _gol_cycle
})


def _gol_help_handler(command_terms):
    response = ''
    if len(command_terms) == 1:
        response = 'gol help displayed in the following format:\n"gol Command": Help_for_command\n'
        for command in GOL_COMMANDS:
            response += '\n"' + command['start'] + '": ' + command['help']
        response += '\n\nUse `gol help COMMAND` to get more help on specific commands.'
    else:
        for command in GOL_COMMANDS:
            if command['start'] == command_terms[1]:
                response = command['specific_help']
                break
        else:
            response = 'Unknown game of life help command. Use "gol help" to get a list of commands.'
    return response

def _gol(client, message, user_command):
    command_terms = user_command.split(' ')[1:]
    response = ''
    if command_terms[0] == 'help':
        response = _gol_help_handler(command_terms)
    else:
        for command in GOL_COMMANDS:
            if command['start'] == command_terms[0].lower():
                response = command['func'](command_terms, str(message.server))
    return client.send_message(message.channel, response)

COMMANDS.append({
    'start': 'gol',
    'help': 'Game of life genetic algorithm commands.',
    'func': _gol
})