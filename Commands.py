"""My EniBot command list. If you have an idea for a command, get in touch!"""
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