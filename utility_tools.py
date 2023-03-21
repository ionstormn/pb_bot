class DataUtility():
    
    def __init__(self, conn):
        '''
        As all functions will need to access redis, it is required to supply a data connection
        '''
        self.redis = conn

    # Custom Exceptions
    class DataUtilityIndexException(Exception):
        pass

    class DataUtilityIdException(Exception):
        pass

    # TODO
    # basically consider making game name optional. 
    # get map_list fuction. 
    # Consider how game can be supplied. Is it fully required or is there a way to extend the scope to where it could be optional?
    # The concept of how to manage passing in the key name is interesting. If this is adhoc remade using the patterns or if something else can be done with the existing objects available. Does this location become a new location of managing the redis key patterns and variables? unlikely. Could just require a maplist to be passed in and make this hyper generic.
    # How Cursed would it be to have data_list be optional, and if None, load from the redis_key?

    def get_id(self, name, data_list):
        _id = None
        try:
            for data in data_list:
                if data['name'] == name:
                    _id = data['id']
        except:
            # I think this is kinda working?
            print(f'[ERROR] {data_list} seems to be invalid. Validate "name" and "id" fields.')
            raise self.DataUtilityIdException('Failed to process data_list')
        return _id

    def get_map_id(self, game, map_name, map_list=None):
        if not map_list:
            map_list_key = f'{game}:map_list'
            map_list = self.redis.json().get(map_list_key)['maps']
        _id = self.get_id(map_name, map_list)
        return _id

    def get_category_id(self, game, category_name, category_list=None):
        if not category_list:
            category_list_key = f'{game}:categories'
            category_list = self.redis.json().get(category_list_key)['categories']
        _id = self.get_id(category_name, category_list)
        return _id

    def get_index(self, data_list, _id=None, name=None):
        # Args should already be validated at this point.
        # Id Is expected to be a integer rather than a string.
        
        try:
            for index, data in enumerate(data_list):
                if _id == data['id']:
                    return index
                if name == data['name']:
                    return index
        except self.DataUtilityIndexException as e:
            print(f'[ERROR] Failure to parse data_list. data_list:[{data_list}]')
            print(e)
            exit(1)
        
        print(f'Unable to find index with params: id:[{_id}] name:[{name}]')
        return None

    def get_map_index(self, game, map_list=None, map_id=None, map_name=None):
        '''
        Using map_name or map_id, determine the index of the map in the redis map list.
        map_list will be generated if not supplied.
        Requires map_id or map_name to be set. If neither are provided, an exception will be raised.
        '''
        if not map_id and not map_name:
            raise self.DataUtilityIndexException('map_id or map_name argument not found. Ensure you are passing at least one of these.')
        if not map_list:
            # Consider having a map of data in redis that can store the key values for easy lookup across classes. 
            map_list_key = f'{game}:map_list'
            map_list = self.redis.json().get(map_list_key)['maps']
        index = self.get_index(map_list, map_id, map_name)
        return index

    def get_category_index(self, game, category_list=None, category_id=None, category_name=None):
        '''
        Using category_name or category_id, determine the index of the category in the redis category list.
        category_list will be generated if not supplied.
        Requires category_id or category_name to be set. If neither are provided, an exception will be raised.
        '''
        
        if not category_id and not category_name:
            raise self.DataUtilityIndexException('category_id or category_name argument not found. Ensure you are passing at least one of these.')
        if not category_list:
            category_list_key = f'{game}:categories'
            category_list = self.redis.json().get(category_list_key)['categories']
        index = self.get_index(category_list, category_id, category_name)
        return index