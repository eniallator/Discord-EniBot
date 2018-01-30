"""Commands todo with minecraft"""
import re
import random
from src.CommandSystem import CommandSystem

MINECRAFT_COMMANDS = CommandSystem()


COLOURS = [hex(n)[2:] for n in range(16)]

async def _ran_colours(client, user_command, message):
    str_input = ' '.join(user_command.split(' ')[2:])
    output = ''
    last_colour = None
    for char in list(str_input):
        if not re.search(r'\s', char):
            colour_choice = random.choice(list(set(COLOURS) - set([last_colour])))
            output += '&' + colour_choice
            last_colour = colour_choice
        output += char
    await client.send_message(message.channel, output)

MINECRAFT_COMMANDS.add_command(
    'ran_colours',
    cmd_func=_ran_colours,
    cmd_help='Inserts random colours for each character.'
)
