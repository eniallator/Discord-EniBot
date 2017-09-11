"""My EniBot command list. If you have an idea for a command, get in touch!"""
from GOL_Sim.GOL_Simulation import GOL_Simulation

CURR_GOL_SIM = GOL_Simulation()

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

def _gol_sim_new(command_terms):
    params = command_terms[1:]
    response = ''
    for index, term in enumerate(params):
        try:
            int(term)
        except:
            response += 'The term at index ' + str(index + 2) + ' has to be a number.\n'
    
    if len(params) > 6:
        response += 'Expecting 6 or less terms'
    
    if not response:
        CURR_GOL_SIM = GOL_Simulation(*params)
        response = 'Successfully created a new game of life genetic algorithm.'
    
    return response

GOL_COMMANDS.append({
    'start': 'new',
    'help': 'Create a new game of life genetic algorithm.',
    'specific_help': 'Where all arguments are optional and all are numbers.\nUsage: `gol_sim new size width height iterations mutation_chance creatures_to_remain`',
    'func': _gol_sim_new
})

def _gol_sim_next_cycle(command_terms):
    CURR_GOL_SIM.evaluate()
    response = CURR_GOL_SIM.stats()
    CURR_GOL_SIM.evolve_population()
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
                response = command['func'](command_terms)
    return client.send_message(message.channel, response)

COMMANDS.append({
    'start': 'gol_sim',
    'help': 'Game of life genetic algorithm commands',
    'func': _gol_sim
})