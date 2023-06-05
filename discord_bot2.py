import discord
from discord.ext import commands

class DiscordBot(commands.Bot):
    intents = discord.Intents.default()
    intents.message_content = True

    def __init__(self):
        super().__init__(command_prefix = '!', intents=self.intents)
        self.wrapper()

    def wrapper(self):
        @self.event
        async def on_message(message):
            print(f'Some Message: {message.content}')

        @self.event
        async def on_ready():
            print(f'Bot Initialized Successfully. Connected as {self.user}')