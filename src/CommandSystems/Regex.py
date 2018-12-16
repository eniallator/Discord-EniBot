import re
from src.CommandSystem import CommandSystem


def _check_server(client, user_command, message):
    return message.server is not None

REGEX_COMMANDS = CommandSystem(help_summary='Commands to do with the regex system.', check_perms=_check_server)
STATE = {}


async def _ask(client, user_command, message):
    server_id = message.server.id
    user_id = message.author.id
    if server_id not in STATE:
        STATE[server_id] = {}
    if user_id not in STATE[server_id]:
        STATE[server_id][user_id] = {}

    regex = ' '.join(user_command.split(' ')[2:])
    STATE[server_id][user_id] = re.compile(regex)
    await client.send_message(message.channel, 'Successfully submitted a regex challenge.')

REGEX_COMMANDS.add_command(
    'ask',
    cmd_func=_ask,
    help_summary='Submit a regex expression for others to solve'
)


def _get_user_id(user_command):
    match = re.match(r'<@!?(?P<id>\d*)>', user_command)
    return match.group('id') if match else None

def _get_longest_match(submission, pattern):
    longest_match, index = 0, 0

    while index < len(submission) - longest_match:
        match = pattern.search(submission, index)
        if not match:
            break

        span = match.span()
        longest_match = span[1] - span[0]
        index = span[1] if span[1] > index else index + 1

    return longest_match

async def _answer(client, user_command, message):
    server_id = message.server.id
    user_id = _get_user_id(user_command.split(' ')[2])

    if user_id is None:
        await client.send_message(message.channel, 'Error you need to mention the person who\'s regex you\'re answering.')
        return
    if server_id not in STATE or user_id not in STATE[server_id]:
        await client.send_message(message.channel, 'Error the user has not submitted a regex challenge before.')
        return

    longest_match = _get_longest_match(
        ' '.join(user_command.split(' ')[3:]),
        STATE[server_id][user_id]
    )
    if longest_match == 0:
        await client.send_message(message.channel, 'Unlucky, there weren\'t any matches this time.')
    else:
        await client.send_message(message.channel, 'The longest match was ' + str(longest_match) + ' characters.')
    

REGEX_COMMANDS.add_command(
    'answer',
    cmd_func=_answer,
    help_summary='Answer someone\'s regex challenge by mentioning them and then the submitted string'
)
