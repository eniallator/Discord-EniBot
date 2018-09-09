"""Commands todo with minecraft"""
import re
import random
from socket import timeout
from discord import Embed
from src.CommandSystem import CommandSystem
from src.minecraftStatusPing import StatusPing

MINECRAFT_COMMANDS = CommandSystem(help_summary='Commands todo with minecraft.')


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
    help_summary='Inserts random colours for each character.'
)

def ping(host, port):
    try:
        port = int(port)
        if port >= 0 and port < 2**16:
            status_ping = StatusPing(host, port)
            return status_ping.get_status()
        else:
            return 'Port out of range.'
    except ValueError:
        return 'Port is not a number.'

async def _get_status(client, user_command, message):
    args = user_command.split(' ')[2:]

    if not args:
        await client.send_message(message.channel, 'Need a server to connect to.')
        return

    if ':' in args[0]:
        args = args[0].split(':')

    host = args[0]
    port = args[1] if len(args) > 1 else '25565'

    try:
        response = ping(host, port)
    except timeout:
        await client.send_message(message.channel, 'Connection timed out.')
        return
    except Exception:
        await client.send_message(message.channel, 'Something went wrong...')
        return

    if isinstance(response, dict):
        player_list = response['players']['sample'] if 'sample' in response['players'] else []
        players_online = [player['name'] for player in player_list]
        embed = Embed(
            title='**' + host + ':' + port + '**',
            type='rich',
            colour=0x32ff32,
            description= re.sub('§.', '', response['description']['text'])
        )
        embed.add_field(
            name='***Player list***',
            value='\n'.join(players_online)
        )
        embed.add_field(
            name='***Players online***',
            value=str(response['players']['online']) + '/' + str(response['players']['max'])
        )
        await client.send_message(message.channel, embed=embed)
    elif isinstance(response, str):
        await client.send_message(message.channel, response)
    else:
        await client.send_message(message.channel, 'Connection timed out.')

MINECRAFT_COMMANDS.add_command(
    'get_status',
    cmd_func=_get_status,
    help_summary='Get the status of any minecraft server. Args: [server IP] [port]'
)
