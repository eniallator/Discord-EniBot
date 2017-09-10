COMMANDS = []

def _ping(client, message):
    return client.send_message(message.channel, 'Pong!')

COMMANDS.append({
    'start': '!ping',
    'func': _ping
})
