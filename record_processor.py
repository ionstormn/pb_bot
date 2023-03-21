import datetime
from utility_tools import DataUtility

class RecordProcessor():
    '''
    Requires a redis connection as part of initialization.
    Intent is to take in args defining a record and write it to the db if valid.
    '''

    def __init__(self, game, redis_conn):
        self.redis = redis_conn
        self.game = game
        self.date = datetime.datetime.now()
        print(self.date)

    def add_record(self, map_name, category_name, record_time):
        record_data = {
            "game": self.game,
            "map_name": map_name,
            "category_name": category_name,
            "record_time": record_time,
            "record_date": self.date
        }

        # Data Validation:
        # Need to expect to have typos and errors in the data sent to this function. It needs to be able to cleanly handle these and reject invalid requests.
        # An easy route is to just call the data utility and pull in the IDs, but we need to wrap some validation logic around this.
        # An expansion of utility will be also searching for aliases for map names, ect. To catch multiple names that result in refering to the same id.
        #   Need to consider how to do this.
        # For Aliasing. Need to init config for maps:0 and categories:0. Then check for the alias key if it exists. If it exists, check this too.
        #   Need to consider how to sync this data. Hashing?

        # How would we get the key to lookup the map:0 id if it needs to search this table for aliases? This actually may need to be on the lookup table afterall.
        # perhaps have a base set of data that isn't flexible, but have a hash key that has some metadata about the config. Can also maybe store a hash value to compare agaisnt.

        print(record_data)