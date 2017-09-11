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
    'help': 'Replies with the source code link',
    'func': _source_code
})

GOL_COMMANDS = []
GOL_INSTANCES = {}
GOL_MAX_PROCESSING = 500000

def _gol_sim_new(command_terms, server):
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
        default_vals = [50, 5, 5, 30]
        accumulator = 1
        for i, val in enumerate(default_vals):
            if len(args) > i:
                accumulator *= args[i]
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
    'specific_help': 'Where all arguments are optional and all are numbers.\nUsage: `gol_sim new size width height iterations mutation_chance creatures_to_remain`',
    'func': _gol_sim_new
})

def _gol_sim_next_cycle(command_terms, server):
    response = ''
    if server and server in GOL_INSTANCES:
        curr_sim = GOL_INSTANCES[server]
        curr_sim.evaluate()
        response = curr_sim.stats()
        curr_sim.evolve_population()
    else:
        response = 'Game of life instance does not exist. To create, use `gol_sim new`'
    return response

GOL_COMMANDS.append({
    'start': 'next_cycle',
    'help': 'Evolves the population and gives stats for the population',
    'specific_help': 'Receives no arguments.\nFirst it will evaluate and then it will get the stats after evaluation and finally evolve the population',
    'func': _gol_sim_next_cycle
})

def _gol_sim_help_handler(command_terms):
    response = ''
    if len(command_terms) == 1:
        response = 'gol_sim help displayed in the following format:\n"gol_sim Command": Help_for_command\n'
        for command in GOL_COMMANDS:
            response += '\n"' + command['start'] + '": ' + command['help']
        response += '\n\nUse `gol_sim help COMMAND` to get more help on specific commands.'
    else:
        for command in GOL_COMMANDS:
            if command['start'] == command_terms[1]:
                response = command['specific_help']
                break
        else:
            response = 'Unknown game of life help command. Use "gol_sim help" to get a list of commands.'
    return response

def _gol_sim(client, message, user_command):
    command_terms = user_command.split(' ')[1:]
    response = ''
    if command_terms[0] == 'help':
        response = _gol_sim_help_handler(command_terms)
    else:
        for command in GOL_COMMANDS:
            if command['start'] == command_terms[0].lower():
                response = command['func'](command_terms, str(message.server))
    return client.send_message(message.channel, response)

COMMANDS.append({
    'start': 'gol_sim',
    'help': 'Game of life genetic algorithm commands',
    'func': _gol_sim
})