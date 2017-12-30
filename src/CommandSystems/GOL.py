"""The game of life commands"""
from GOL_Sim.GOL_Simulation import GOL_Simulation
from src.CommandSystem import CommandSystem

GOL_COMMANDS = CommandSystem()

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

async def _gol_new(client, command_terms, message):
    string_args = command_terms.split(' ')[2:]
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
    
    await client.send_message(message.channel, response)

GOL_COMMANDS.add_command(
    'new',
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

async def _gol_next_cycle(client, command_terms, message):
    response = _validate_gol_instance(str(message.server))
    if not response:
        response = _cycle_instance(GOL_INSTANCES[str(message.server)])
    await client.send_message(message.channel, response)

GOL_COMMANDS.add_command(
    'next_cycle',
    cmd_func=_gol_next_cycle,
    cmd_help=lambda client, user_cmd, message: 'Evolves the population and gives stats for the population.',
    specific_help=lambda client, user_cmd, message: 'Receives no arguments.\nFirst it will evaluate and then it will get the stats after evaluation and finally evolve the population.'
)


PROGRESS_MESSAGE = {}
PROGRESS_MESSAGE['format'] = lambda curr, limit: 'Progress: ' + str(curr / limit * 100)[:5] + '%'

async def _send_progress(client, message, curr, limit):
    if PROGRESS_MESSAGE['new_message']:
        PROGRESS_MESSAGE['new_message'] = False
        PROGRESS_MESSAGE['message'] = await client.send_message(message.channel, PROGRESS_MESSAGE['format'](curr, limit))
    else:
        PROGRESS_MESSAGE['message'] = await client.edit_message(PROGRESS_MESSAGE['message'], PROGRESS_MESSAGE['format'](curr, limit))

async def _gol_cycle(client, command_terms, message):
    response = ''
    response = _validate_gol_instance(str(message.server))
    PROGRESS_MESSAGE['new_message'] = True
    if not response:
        try:
            max_iterations = int(command_terms.split(' ')[2])
            if 1 <= max_iterations <= GOL_MAX_CYCLES:
                for i in range(max_iterations):
                    response = _cycle_instance(GOL_INSTANCES[str(message.server)])
                    if i < max_iterations - 1:
                        await _send_progress(client, message, i + 1, max_iterations)
                if PROGRESS_MESSAGE['message']:
                    await client.delete_message(PROGRESS_MESSAGE['message'])
            else:
                response = 'Limit out of range. Choose an integer between 1-' + str(GOL_MAX_CYCLES) + '.'
        except ValueError:
            response = 'The second argument has to be an integer between 1-' + str(GOL_MAX_CYCLES) + '.'
    await client.send_message(message.channel, response)

GOL_COMMANDS.add_command(
    'cycle',
    cmd_func=_gol_cycle,
    cmd_help=lambda client, user_cmd, message: 'Evolves the population a number of times and gives stats for the population afterwards.',
    specific_help=lambda client, user_cmd, message: 'Receives 1 argument; a number from 1-' + str(GOL_MAX_CYCLES) + ' to cycle through the simulation.\n Usage: `gol cycle limit`'
)
