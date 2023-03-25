import datetime
from utility_tools import DataUtility

class RecordProcessor():
    '''
    Requires a redis connection as part of initialization.
    Intent is to take in args defining a record and write it to the db if valid.
    '''

    class UnknownMapException(Exception):
        pass
    class UnknownCategoryException(Exception):
        pass

    def __init__(self, game, redis_conn):
        self.redis = redis_conn
        self.game = game
        self.date = datetime.datetime.now()

    def validate_record_time(self, record_time):
        # This is a case where we would need multiple potential formats. If an hour is popped in here, it will fail.
        # Could optionally test both and pick what passes....
        # Could also add a millisecond precision config option.
        # [TODO] This needs to be expanded to support custom formats and multiple formats to validate. For ex: Long surf times.
        time_format = '%M:%S.%f'
        time = datetime.datetime.strptime(record_time, time_format)
        formatted_time = time.strftime(time_format)[:-3]
        return formatted_time


    def add_record(self, map_name, category_name, record_time):
        record_time = self.validate_record_time(record_time)

        record_data = {
            "record_id": None,
            "game": self.game,
            "map_name": map_name,
            "map_id": DataUtility(conn=self.redis).get_map_id(game=self.game, map_name=map_name),
            "category_name": category_name,
            "category_id": DataUtility(conn=self.redis).get_category_id(game=self.game, category_name=category_name),
            "record_time": str(record_time),
            "record_date": str(self.date)
        }

        if not record_data['map_id']:
            raise self.UnknownMapException(f'Unknown Map: {map_name}')
        if not record_data['category_id']:
            raise self.UnknownCategoryException(f'Unknown Category: {category_name}')

        # Validations Have Passed. Assign a record id.
        record_id_key = f'{self.game}:record_id_seq'
        record_data['record_id'] = self.redis.incr(record_id_key)

        # Updating Data Store with Record.
        map_key = f'{self.game}:{record_data["map_id"]}:{record_data["category_id"]}'
        print(f'Adding Record to [{map_key}]: {record_data}')
        self.redis.json().arrappend(map_key, '$.records', record_data)

        # Validation:
            # How do we get the time format and convert it?
                # This will be very complicated. Will need to add a redis key for general game config and put it in there.
            # What's the standard format for the date entry?
            # Do we need an id?
            # how would we assume this is used in the bot code? sending a context object?