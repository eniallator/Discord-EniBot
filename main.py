import asyncio
import discord
from time import gmtime, strftime
import Credentials
from Commands import COMMANDS

CLIENT = discord.Client()

def _get_time():
    raw_time = strftime("%Y/%m/%d %H:%M:%S", gmtime())
    return '[' + raw_time + '] '

@CLIENT.event
async def on_ready():
    print('Logged in as')
    print(CLIENT.user.name)
    print(CLIENT.user.id)
    print('------')

@CLIENT.event
async def on_message(message):
    if str(message.channel) == 'bot_testing' and not message.author.bot:
        for command in COMMANDS:
            if message.content.lower().startswith(command['start']):
                print(_get_time() + str(message.author) + ' ran: "' + message.content + '" in server: ' + message.server.name)
                await command['func'](CLIENT, message)
                break

CLIENT.run(Credentials.TOKEN)
