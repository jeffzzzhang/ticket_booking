import pymongo
from constant import constant as cnst

def db_init():
    jd = {
         "packages": [
                    { "id": 1, "flight": "Flight-1", "stay": "2022-08-09", "price": 100, 'quota': 1 },
                    { "id": 2, "flight": "Flight-2", "stay": "2022-08-09", "price": 100, 'quota': 2 },
                    { "id": 3, "flight": "Flight-3", "stay": "2022-08-10", "price": 100, 'quota': 2 },
                    { "id": 4, "flight": "Flight-3", "stay": "2022-08-11", "price": 100, 'quota': 2 }
                ]
                }
    with pymongo.MongoClient(f"""mongodb://{cnst.mongo_host}:{cnst.mongo_port}/""") as c:
        mdb = c[cnst.mongo_db]
        coll = mdb[cnst.mongo_coll]
        x = coll.insert_many(jd['packages'])
        print(x.inserted_ids)

        #coll_order = mdb[cnst.mongo_coll_order]
    print('mongoDB collection initialisation: DONE')


if __name__ == '__main__':
    db_init()
