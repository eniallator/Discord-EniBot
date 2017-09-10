import asyncio
import discord
import Credentials
from Commands import COMMANDS

CLIENT = discord.Client()

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
                print('"' + message.content + '" ran as command')
                await command['func'](CLIENT, message)
                break

CLIENT.run(Credentials.TOKEN)
