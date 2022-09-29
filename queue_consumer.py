import os
import json
import time
import logging
import redis
import pymongo
from constant import constant as cnst

def consumer_():
    redis_pool = redis.ConnectionPool(host='localhost', port= 6379)
    with redis.Redis(connection_pool= redis_pool) as redis_conn:
        while True:
            if redis_conn.llen('queue') > 0:
                tmp = json.loads(redis_conn.rpop('queue').decode())
                logging.info("element popped out from queue"+str(tmp['id']))
                cond = {'id': tmp['id'], 'quota': {'$gt': 0}}
                with pymongo.MongoClient(mongo_url) as mcl:
                    # db.testdb.update({'b':106}, {$push: {'al': 99}})
                    coll = mcl[cnst.mongo_db][cnst.mongo_coll]
                    res = coll.find_one(cond)
                    if not res:
                        return 'No available package for the reservation'
                    quota_decr = {'$inc': {'quota': -1}}
                    # update quota
                    _ = coll.update_one(cond, quota_decr)
                    # insert order info
                    if not coll.find_one({'id': tmp['id'], 'email_id': tmp['email_id']}):
                        _ = coll.insert_one(tmp)
                    else:
                        # duplicate order, simply reject
                        return 'OrderError: You had made a reservation'
            else:
                logging.info('NO ELEMENT IN QUEUE, SLEEP FOR 5 SECONDS')
                time.sleep(5)
        return 'Done'

if  __name__ == '__main__':
    mongo_url = f"""mongodb://{cnst.mongo_host}:{cnst.mongo_port}/"""
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.DEBUG)
    consumer_()