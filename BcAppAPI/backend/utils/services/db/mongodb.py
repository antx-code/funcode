from pymongo import MongoClient
from loguru import logger
import bson
# from PIL import Image
from io import StringIO, BytesIO
from bson.objectid import ObjectId
import base64

logger.add(sink='logs/mongodb.log',
           level='ERROR',
           # colorize=True,     # 设置颜色
           format='{time:YYYY-MM-DD  :mm:ss} - {level} - {file} - {line} - {message}',
           enqueue=True,
           # serialize=True,    # 序列化为json
           backtrace=True,   # 设置为'False'可以保证生产中不泄露信息
           diagnose=True,    # 设置为'False'可以保证生产中不泄露信息
           rotation='00:00',
           retention='7 days')


class MongoDB():
    @logger.catch(level='ERROR')
    def __init__(self, db, col):
        """
        initial the mongodb and select the database and collection.
        :param db: The database that you want to operate.
        :param col: The collection that you want to opreate.
        """
        client = MongoClient(connect=False)
        try:
            self.database = client[db]
        except Exception as e:
            logger.error(e)
            logger.add(e)
            logger.error('Has error when operate database')
        try:
            self.collection = self.database[col]
        except Exception as e:
            logger.error(e)
            logger.add(e)
            logger.error('Has error when operate collection')


    @logger.catch(level='ERROR')
    def insert_one_data(self,data_dict):
        """
        onsert one data into the mongodb.
        :param data_dict:
        :return:
        """
        self.collection.insert_one(data_dict)


    @logger.catch(level='ERROR')
    def insert_many(self,data_dict_list):
        """
        insert many data into the mongodb.
        :param data_dict: A list of data dictionary that you want to insert.
        :return:
        """
        self.collection.insert_many(data_dict_list)
        # return True


    @logger.catch(level='ERROR')
    def query_data(self,data_dict={},skip=None, limit=None):
        """
        query the account info from mongodb.
        :param data_dict: The query parm dictionary, and it's default value is {},which means to find all value
        :return: user_dict: Return a cursor of the data object.
        """
        # self.de_same_data(data_dict)
        if limit is not None and skip is not None:
            user_dict = self.collection.find(data_dict).skip(skip).limit(limit)
        else:
            user_dict = self.collection.find(data_dict)
        return user_dict


    @logger.catch(level='ERROR')
    def find_one(self, data_dict: str, ori_id=False):
        return self.collection.find_one(data_dict, {'_id':0})


    @logger.catch(level='ERROR')
    def dep_data(self, parm):
        """
        Return duplicate data with the query parm.
        :param parm: The parameter that you want to as a basis to duplicate the data.
        :return: dep_data: Return a list of after duplicate data. It's only include the duplicate parameter datas.
        """
        dep_data = self.collection.distinct(parm)
        return dep_data


    @logger.catch(level='ERROR')
    def delete_one(self, data_dict):
        """
        delete one special data from mongodb.
        :param data_dict:
        :return:
        """
        self.collection.delete_one(data_dict)


    @logger.catch(level='ERROR')
    def update_one(self, query_dict, new_data_dict):
        """
        Update an exist data.
        :param query_dict: A dictionary of the segment that you want to update.
        :param new_data_dict: The new data dictionary that you want to replace the origin data.
        :return:
        """
        self.collection.update_one(query_dict, {'$set':new_data_dict}, upsert=True)
        return True


    @logger.catch(level='ERROR')
    def drop_collection(self):
        """
        Drop the current collection.
        :return: A bool vaule of the operate.
        """
        self.collection.drop()
        return True


    @logger.catch(level='ERROR')
    def rename_collection(self, new_name):
        """
        Rename the current collection.
        :param new_name: The new collection that you want to rename.
        :return: A bool value of the operate.
        """
        self.collection.rename(new_name)
        return True

    @logger.catch(level='ERROR')
    def save_img(self, user_id, img, img_name='img', qr_code=False):
        # save_data = self.collection.save(dict(user_id = user_id, img = bson.binary.Binary(img_content.getvalue())))
        try:
            save_data = base64.b64encode(bson.binary.Binary(img.getvalue())).decode('ascii')
        except Exception as e:
            save_data = base64.b64encode(bson.binary.Binary(img)).decode('ascii')
        if not qr_code:
            self.collection.update_one({'user_id': user_id}, {"$set": {f'{img_name}': save_data}}, upsert=True)
        else:
            self.collection.update_one({'user_id': user_id},
                                       {"$set": {f'promo_code': img_name, 'promo_qrcode': save_data}}, upsert=True)
        return save_data


    @logger.catch(level='ERROR')
    def read_img(self, user_id, img_name=None, save_local=False):
        """
        Read the image information from mongodb and save it into a picture in the current directory.
        :param img_id: The image id which you want to saved, and it's value is the mongodb image id.
        :param img_name: The name you want to saved, it must be include a format.
        :return: A bool value of the operate.
        """
        # fs = GridFS(self.database)
        # result = fs.get(img_oid).read()
        # return result
        data = self.collection.find_one({'user_id': user_id})
        img = data['img']
        # image = Image.open(BytesIO(return_data))

        # md5 = hashlib.md5()
        # hash_data = md5.update(return_data.encode('utf-8'))
        if save_local:
            with open(img_name, 'wb') as f:
                f.write(img)
        return img


    @logger.catch(level='ERROR')
    def aggregate_dep_data(self, condition, match_condition='gt', delete=False):
        """
        Duplicate the big data asset and return a list of repeat data, which the distinct operate is nor work condition.
        :param condition: The duplicate condition
        :param match_condition: The match condition of the aggregate query, and it's default value is eq. It can be eq, gt, lt and etc.
        :param delete: The tag of the query, if delete is True, it will delete the repeat data, and it's default value is True.
        :return: result: A list of the repeat data.
        """
        pipeline = [
            {
                '$group': {
                    '_id': {condition: f'${condition}'},
                    'count': {'$sum': 1},
                    'dups': {
                        '$addToSet': '$_id'
                    }
                },
            },
            {
            '$match': {
                    'count': {
                        f'${match_condition}': 1
                    }
                }
            }
        ]
        result = list(self.collection.aggregate(pipeline=pipeline))
        if delete:
            if len(result) > 0:
                for each_repeat in result:
                    for i in range(0, each_repeat['count']-1):
                        # print(f'ObjectId("{each_repeat["dups"][i]}")')
                        obj_id = each_repeat["dups"][i]
                        # print(self.collection.find_one({'_id':ObjectId(obj_id)}))
                        self.delete_one({'_id':ObjectId(obj_id)})
        return result

    @logger.catch(level='ERROR')
    def data_count(self, query_dict):
        data_count = self.collection.count_documents(query_dict)
        return data_count