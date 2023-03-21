import redis
from redis.commands.json.path import Path
import yaml
import record_processor
from utility_tools import DataUtility
from record_processor import RecordProcessor

# This test will implement the new conceptual architecture.
# Plan:
# 0. Mock JSON data structures for Maps, Categories, and Records.
# - How would this align to OM schemas? 
# 0. Mock redis keys.
# 1. Create config parser that creates map data.
# 2. Create config parser that creates category data.
# 3. Load Initial test data using the new format. Determine if initial load should create json data that has no records. Or if this is feasible during creation of the first record.
# 4. Implement process for determining how to handle reloads of config. initialization, ect. 
# 5. Identify process for breaking down process into multi-game structures. For example, when and how config is loaded for each loaded game.


class ConfigInit():
    '''
    game = The game to be initialized from Config.
    conn = An object containing an active Redis connection pool.
    '''
    def __init__(self, game, redis_conn):
        self.game = game
        self.redis = redis_conn

        # Load and Parse Config
        self.config_data = self.load_config()
        self.config_game_name = self.config_data['game']
        self.config_game_maps = self.config_data['maps']
        if 'categories' in self.config_data:
            self.config_game_categories = self.config_data['categories']
        else:
            self.config_game_categories = None

        # Setup Redis Key Name Values.
        self.map_id_key = f'{game}:map_id_seq'
        self.category_id_key = f'{game}:category_id_seq'

        self.game_map_list_key = f'{game}:map_list'
        self.game_maps_key = f'{game}:maps'
        self.game_categories_key = f'{game}:categories'

    def init_config(self):
        self.init_map_list()
        self.load_map_list()
        self.init_categories()
        self.init_maps()

    # NOTE: For all active games, load config and validate schema state compared to config. Adding new maps, categories, ect.  This is an initialization process. 
    # Load Game Configuration
    def load_config(self):
        try:
            print(f"Loading {self.game} Config Data...")
            with open(f"test_data/{self.game}_config.yml", 'r') as data_file:
                data = yaml.load(data_file, Loader=yaml.FullLoader)
        except Exception as e:
            print(e)
            print("Unable to load data file.")
            exit(1)
        return data

    # Setup Maps First
    ## Avoid Aliases, and Focus on pattern to generate IDs and add data if it's missing. Need to solution updating config if there was a config change. Ideally need to be able to edit data in line. Instead of pop/push.
    ## This is making a lookup table very appealing. 
    # Also no data sanitization right now, someone can pop in almost anything here... Very bad. Need to validate and only select approved fields.

    # Add Map to map_list then create the entry under {game}:{maps}:{id}. If Map exists in lookup table, skip. This is where we can add functionality to update the map data more cleanly.


    # Consider how this can be made more available since it will likely need to be used in the runtime class.
    # Maybe apart of the helper class by getting it to refresh cache before returning gets. Requires to pass in game.
    def update_local_cache(self, key_type):
        match key_type:
            case 'map_list':
                self.map_list = self.redis.json().get(self.game_map_list_key)
            case 'category_list':
                self.category_list = self.redis.json().get(self.game_categories_key)
            case _:
                raise Exception(f'Uknown key_type passed to update function. {key_type}')

    def init_map_list(self):
        map_list = self.redis.json().get(self.game_map_list_key)
        if not map_list:
            print('Empty Map List Detected. Performing Initialization.')
            map_list = {'maps': []}
            self.redis.json().set(self.game_map_list_key, Path.root_path(), map_list)
        self.update_local_cache('map_list')

    def load_map_list(self):
        for game_map in self.config_game_maps:
            map_id = DataUtility(self.redis).get_map_id(game=self.game, map_list=self.map_list['maps'], map_name=game_map['name'])
            if map_id:
                map_index=DataUtility(self.redis).get_map_index(game=self.game, map_list=self.map_list['maps'], map_id=map_id)
                print(f'Found Map: { self.map_list["maps"][map_index] }')
            else:
                print(f'[{game_map["name"]}] Map Not Found In Map List Table. Creating.')
                map_id = self.redis.incr(self.map_id_key)
                # Probably Add some ID sanity checks. For ex. Making sure no duplicates.
                self.redis.json().arrappend(self.game_map_list_key, '$.maps', {'id': map_id, 'name': game_map['name']})
                print(f'[{game_map["name"]}][id:{map_id}] Map Created.')
        self.update_local_cache('map_list')


    # This method is extremely bloated and messy. Needs to be cleaned up. Need to split this into more generic functions in a refactor.
    def init_categories(self):
        # Check Redis key and set base structure if it is not present.
        self.category_list = self.redis.json().get(self.game_categories_key)
        if not self.category_list:
            print('Empty Category List. Performing Initialization.')
            category_list = {'categories': []}
            self.redis.json().set(self.game_categories_key, Path.root_path(), category_list)
            self.update_local_cache('category_list')

        if not self.config_game_categories:
            # Check to see if default has already been created.
            category_id = DataUtility(self.redis).get_category_id(game=self.game, category_list=self.category_list['categories'], category_name='default')
            if category_id:
                category_index = DataUtility(self.redis).get_category_index(game=self.game, category_list=self.category_list['categories'], category_id=category_id)
                print(f'Found Category: { self.category_list["categories"][category_index] }')
            else:
                print('No Explicit Categories found. Initializing default category')
                category_id = self.redis.incr(self.category_id_key)
                self.redis.json().arrappend(self.game_categories_key, '$.categories', {'id': category_id, 'name': 'default'})
        else:
            for category in self.config_game_categories:
                category_id = DataUtility(self.redis).get_category_id(game=self.game, category_list=self.category_list['categories'], category_name=category['name'])
                if category_id:
                    category_index = DataUtility(self.redis).get_category_index(game=self.game, category_list=self.category_list['categories'], category_id=category_id)
                    print(f'Found Category: { self.category_list["categories"][category_index] }')
                else:
                    print(f'[{category["name"]}] Category Not Found In Category List Table. Creating.')
                    category_id = self.redis.incr(self.category_id_key)
                    self.redis.json().arrappend(self.game_categories_key, '$.categories', {'id': category_id, 'name': category['name']})
                    print(f'[{category["name"]}][id:{category_id}] Category Created.')
        self.update_local_cache('category_list')

# Now need to create individual map data under <game>:maps:id
## This should be apart of the init.. right?
    def init_maps(self):
        '''
        For each map in the map_list, check if a primary record has been created for each category and create the base object if needed.
        This initializes the base data that will hold the record object list. This avoids the record processing being required to both check and create this data when it should primarily focus on processing records.
        '''
        print(f'[{self.game}] Initializing Map Record Data..')
        for _map in self.map_list['maps']:
            for _category in self.category_list['categories']:
                # Check to see if the base object exists in redis.
                # <game>:<map_id>:<category_id>: <JSON Data>`
                redis_key = f'{self.game}:{_map["id"]}:{_category["id"]}'
                _data = self.redis.json().get(redis_key)
                map_category_name = f'{_map["name"]}:{_category["name"]}'
                if _data:
                    print(f'Found Record Data: [{map_category_name}] key:[{redis_key}]')
                else:
                    print(f'No Record Data Found for [{map_category_name}]. Initializing..')
                    self.redis.json().set(redis_key, Path.root_path(), {'game':             self.game, 
                                                                        'map_id':           _map["id"], 
                                                                        'map_name':         _map['name'], 
                                                                        'category_id':      _category["id"], 
                                                                        'category_name':    _category["name"], 
                                                                        'records':          []})
                    print(f'Record Data Initialized for [{map_category_name}] key:[{redis_key}]')