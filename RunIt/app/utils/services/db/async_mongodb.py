from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from init import config

class AsyncMongo():
    @logger.catch(level='ERROR')
    def __init__(self, db, col, port=27017):
        """

        Init the mongodb with asyncio method.

        :param db: The mongodb name.
        :param col: The collection of the mongodb.
        """
        conf = config["MONGO"]
        client = AsyncIOMotorClient(conf["ADDRESS"], port)
        # client = AsyncIOMotorClient(f'mongodb://{conf["USERNAME"]}:{conf["PASSWORD"]}@{conf["ADDRESS"]}:{port}')
        database = client[db]
        self.collection = database[col]

    @logger.catch(level='ERROR')
    async def query_mongo(self, query_cmd={}, skip=0, limit=10, sort_key='-_id'):
        """

        Query the mongodb data and return a list of the data. It's default return value is all the relation data.

        :param data_dic: The query parameter, it's default value is {}, which is mean query all data.
        :return: data_list: Return a list of the query.
        """
        data_list = []
        if '-' not in sort_key:
            order = sort_key
        else:
            order = sort_key[1:]
        logger.info(f'sort key -> {order}')
        async for data in self.collection.find(query_cmd, {'_id':0}).sort(order, -1).skip(skip).limit(limit):
            data_list.append(data)
        total_count = await self.collection.count_documents(query_cmd)
        return data_list, total_count

    @logger.catch(level='ERROR')
    async def dep_data(self, mongo_parm):
        """

        Query the distinct data with a less than 16MB size data.

        :param mongo_parm: The distinct query parameter.
        :return: date_list: Return a data list of the query.
        """
        data_list = []
        result = await self.collection.distinct(mongo_parm)
        for each_data in result:
            data_list.append(each_data)
        return data_list

    @logger.catch(level='ERROR')
    async def aggre(self, pipeline, diskuse=True):
        """

        A high-level query data method, which was called aggregate query.

        :param pipeline: The query parameter, which consist with a list of query sentence.
        :return: daat_list: Return a data list of the query.
        """
        data_list = []
        async for doc in self.collection.aggregate(pipeline=pipeline, allowDiskUse=diskuse):
            del doc['_id']
            data_list.append(doc)
        return data_list

    @logger.catch(level='ERROR')
    async def get_count_docs(self, query_dic):
        result = await self.collection.count_documents(query_dic)
        return result