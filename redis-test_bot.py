import redis
from redis.commands.json.path import Path
import yaml
from utility_tools import DataUtility
from record_processor import RecordProcessor
from config_init import ConfigInit

class PB_Bot():
    def __init__(self):
        self.main()

    def load_core_config(self):
        # Loading Base Config
        try:
            print("Loading Core Config...")
            with open("config.yml", 'r') as config_file:
                config = yaml.load(config_file, Loader=yaml.FullLoader)
        except Exception as e:
            print(e)
            print("Unable to load config.yml. Make sure you created your configuration.")
            exit(1)

        # Setting Discord Roles.
        self.admin_role_enabled  = config["base_config"]["admin_role"]["enabled"]
        self.admin_role_name     = config["base_config"]["admin_role"]["role"]
        self.user_role_enabled   = config["base_config"]["user_role"]["enabled"]
        self.user_role_name      = config["base_config"]["user_role"]["role"]

        # Determine Active Games.
        self.active_channels    = [game['channel'] for game in config['games'] if game['enabled']]
        self.active_games       = [game['name'] for game in config['games'] if game['enabled']]

    def initialize_config(self):
        print(f'Initializing Active Games: [{self.active_games}]')
        for game in self.active_games:
            ConfigInit(game, self.redis_conn).init_config()

    def test_loop(self):
        conn_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self.redis_conn = redis.Redis(connection_pool=conn_pool)
        
        self.initialize_config()
        
        # Fake Runtime
        # This will also include some other meta data sent to the processor. Or we strip it out and only send what is needed.
        # For ex: Discord ID.
        RecordProcessor('mk64', self.redis_conn).add_record('Moo Moo Farm', 'nonsc-3lap', '0:33.55')

    def main(self):
        self.load_core_config()
        self.test_loop()

PB_Bot()