import redis
from redis.commands.json.path import Path
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
import json

conn_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis = redis.Redis(connection_pool=conn_pool)

try:
    print("Loading Data...")
    with open("test_data/mk64_redis_test.json", 'r') as data_file:
        data = json.load(data_file)
except Exception as e:
    print(e)
    print("Unable to load data file.")
    exit(1)

record_schema = (
                TextField("$.game", as_name="game"),
                TextField("$.map", as_name="map"),
                TextField("$.category", as_name="category"),
                # TextField("$.time", as_field="time"),
                # TextField("$.date", as_field="date"),
                TextField("$.player", as_name="player")
                )
index_definition = IndexDefinition(prefix=['records:'], index_type=IndexType.JSON)

try:
    print("Searching for index...")
    redis.ft('record_idx').info()
    print("Index present. Proceeding.")
except:
    print("Unable to find record index... creating it.")
    redis.ft(index_name="record_idx").create_index(record_schema, definition=index_definition)

# #Loading Data
# print(data['data'])
# for record in data['data']:
#     record_id = redis.incr('seq_record_id')
#     redis.json().set(f'records:{record_id}', Path.root_path(), record)

map_test="Bowser's Castle"
print("Search testing...")
#response = redis.ft("record_idx").search('@map:("Bowser\'s Castle") @category:("non_sc_3lap")')
response = redis.ft("record_idx").search(f'@map:({map_test})')
for doc in response.docs:
    doc_data = json.loads(doc.json)
    print(f'Player: [{doc_data["player"]}] - Map: [{doc_data["map"]}] - Time: [{doc_data["time"]}]')
print(response)



