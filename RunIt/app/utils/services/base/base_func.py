import datetime
from bson import ObjectId

def object_id_from_datetime(from_datetime=None):
    ''' According to the time manually generated an ObjectId '''
    if not from_datetime:
        from_datetime = datetime.datetime.now()
    return ObjectId.from_datetime(generation_time=from_datetime)
