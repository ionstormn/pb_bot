import discord
from discord.ext import commands
import yaml

# Loading Base Config
try:
    print("Loading Config...")
    with open("config.yml", 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
except Exception as e:
    print(e)
    print("Unable to load config.yml. Make sure you created your configuration.")
    exit(1)

admin_role_enabled  = config["base_config"]["admin_role"]["enabled"]
admin_role_name     = config["base_config"]["admin_role"]["role"]
user_role_enabled   = config["base_config"]["user_role"]["enabled"]
user_role_name      = config["base_config"]["user_role"]["role"]

# Config Parsing
active_channels = [game['channel'] for game in config['games'] if game['enabled']]
active_games    = [game['name'] for game in config['games'] if game['enabled']]

print(f'Active Channels: [{", ".join(active_channels)}]')
print(f'Active Games: [{", ".join(active_games)}]')

# Bot Init
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents=intents)

# Error Handling Setup
class InvalidChannelCheckFailure(commands.CheckFailure):
    pass

# Bot Basic Events
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Custom Checks
def check_admin_role_config():
    def predicate(ctx):
        return True

    if admin_role_enabled:
        return commands.has_role(admin_role_name)
    else:
        return commands.check(predicate)

def check_user_role_config():
    def predicate(ctx):
        return True

    if user_role_enabled:
        return commands.has_role(user_role_name)
    else:
        return commands.check(predicate)

# Scenario:
# Need to check active games.
# If Game is active, check channel.
# if message came from channel, begin parsing.
# This will serve as a primary entry point for the bot and logic needs to be available for every command, so a generic call is needed.

def determine_valid_channel():
    # More or less, for all enabled games, grab all valid channels and determine if the command should continue.
    # Ideally, an exception that results in a channel message is thrown for channels in the game list.
    # Otherwise, a silent exception should occur to avoid spamming channels that are not bot enabled.
    def predicate(ctx):
        channel_name = ctx.channel.name
        if channel_name in active_channels:
            return True
        else:
            raise InvalidChannelCheckFailure(f'#{channel_name} is not currently active for a game.')
    return commands.check(predicate)

def determine_game(ctx):
    # This logic will be required to be heavily modified when multi-game channel support is added.
    # Since filtering has already been done with determine_valid_channel(), we can hopefully safely assume we do not need to check active status for the game.
    for game in config['games']:
        # This logic breaks when moving to multi-game channels.
        if ctx.channel.name == game['channel']:
            return game['name']

@check_user_role_config()
@determine_valid_channel()
@bot.command()
async def add(ctx, name='add_stuff', **args):
    active_game = determine_game(ctx)
    await ctx.send(f'[{active_game}] Just testing... {args}')

# Error Handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, InvalidChannelCheckFailure):
        await ctx.send(error)
    if isinstance(error, discord.ext.commands.errors.MissingRole):
        await ctx.send(error)

@add.error
async def add_error(ctx, error):
    print(f"Add Command Error. : [{error}]")

# Launch
bot.run(config["base_config"]["auth_token"])
