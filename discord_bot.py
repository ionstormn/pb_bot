import discord
from discord.ext import commands
import yaml

class DiscordBot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix = '!', intents=intents)

    def __init__(self):
        pass

    def start_bot(self, creds):
        self.bot.run(creds)

    @bot.event
    async def on_ready():
        print(f'Bot Initialized Successfully. Connected as {DiscordBot.bot.user}')

    @bot.event
    async def on_message(message):
        print(f'Message: {message.content}')