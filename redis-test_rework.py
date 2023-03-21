import redis
from redis.commands.json.path import Path
import json
import yaml

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


conn_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis = redis.Redis(connection_pool=conn_pool)

game="mk64"

# NOTE: This may be appropriate for a class. Assigning config, categories, tracks as attributes on the return. Maybe not. But this should return either the full payload or a structure with it broken down.
# NOTE: For all active games, load config and validate schema state compared to config. Adding new maps, categories, ect.  This is an initialization process. 
# Load Game Configuration
try:
    print("Loading Data...")
    with open(f"test_data/{game}_config.yml", 'r') as data_file:
        data = yaml.load(data_file, Loader=yaml.FullLoader)
except Exception as e:
    print(e)
    print("Unable to load data file.")
    exit(1)

game_name = data['game']
game_maps = data['maps']
game_categories = data['categories']

record_id_key = f'{game}:map_id_seq'
category_id_key = f'{game}:category_id_seq'

# Setup Maps First
## Avoid Aliases, and Focus on pattern to generate IDs and add data if it's missing. Need to solution updating config if there was a config change. Ideally need to be able to edit data in line. Instead of pop/push.
## This is making a lookup table very appealing. 
# Also no data sanitization right now, someone can pop in almost anything here... Very bad. Need to validate and only select approved fields.

game_map_list_key = f'{game}:map_list' # This will contain a lookup table with map names and IDs. The binding will be full map name, Otherwise a new map will be generated. 
game_maps_key = f'{game}:maps'

# Add Map to map_list then create the entry under {game}:{maps}:{id}. If Map exists in lookup table, skip. This is where we can add functionality to update the map data more cleanly.

## Check Lookup Table for Data.
map_list = redis.json().get(game_map_list_key)
if not map_list:
    print('Empty Map List Detected. Performing Initialization.')
    map_list = {'maps': []}
    redis.json().set(game_map_list_key, Path.root_path(), map_list)
print(map_list)


# These helper functions will likely be critical, and also need to be more generic. map_list can probably just be another redis call instead of passing this data around. Especially if it can become stale.
def get_map_id(map_name, map_list):
    '''
    Get map id based on map name by searching the maplist.'''
    _map_id = None
    for _map in map_list['maps']:
        if _map['name'] == map_name:
            _map_id = _map["id"]
    return _map_id

def get_map_index(map_list, map_id=None, map_name=None):
    '''
    Using map_name or map_id, determine the index of the map in the redis map last.
    '''
    
    if not map_id and not map_name:
        raise Exception('map_id or map_name argument not found. Ensure you are passing at least one of these.')

    for index, data in enumerate(map_list['maps']):
        # Add Code to check for dupes before returning index.
        # If Map_id is supplied, utilize this over the map_name.
        if map_id == data['id']:
            return index
        elif map_name == data['name']:
            return index
    
    # At this point, The map has not been found and a raise is returned.
    raise Exception('Unable to find map index.')

for game_map in game_maps:
    map_id = get_map_id(game_map['name'], map_list)
    if map_id:
        print(f'Found Map: { map_list["maps"][get_map_index(map_list, map_id=map_id)] }')
    else:
        print(f'[{game_map["name"]}] Map Not Found In Map List Table. Creating.')
        map_id = redis.incr(record_id_key)
        # Probably Add some ID sanity checks. For ex. Making sure no duplicates.
        redis.json().arrappend(game_map_list_key, '$.maps', {'id': map_id, 'name': game_map['name']})
        print(f'[{game_map["name"]}][id:{map_id}] Map Created.')

# Now need to create individual map data under <game>:maps:id

# Class loop could just be to init a redis connection, loop over active games, and end those objects. Could move the index/map lookup to a helper function that could be in another class. 

# For Categories, Need to initialize a default category if the category key is missing in the yaml. The other alternative was to force someone to add a null and treat it like a native boolean value.

### Class Stuff

