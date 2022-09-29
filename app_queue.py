import os
import json
import time
import random
import logging
import threading
import concurrent.futures
from queue import Queue 
from threading import Thread
from datetime import datetime as dt
import flask
import redis
import pymongo
import pandas as pd
from flask import Flask, request, render_template, send_from_directory,url_for,redirect
from constant import constant as cnst

app = Flask(__name__)

@app.route("/order-queue", methods=["GET", "POST"])
def order_queue():
    # get fundamental information of available quota/tickets
    mongo_url = f"""mongodb://{cnst.mongo_host}:{cnst.mongo_port}/"""
    avail_tickets = []
    with pymongo.MongoClient(mongo_url) as mcl:
        coll = mcl[cnst.mongo_db][cnst.mongo_coll]
        cond = {'quota': {'$gt': 0}}
        avail_quota = coll.find(cond)
        for i in avail_quota:
            avail_tickets.append(i)
    _ = [term.pop('_id') for term in avail_tickets]

    # deal with GET request 
    if flask.request.method == 'GET':
        flights_info = set()
        stay_info = set()
        for i in avail_tickets:
            flights_info.add(i['flight'])
            stay_info.add(i['stay'])
        return render_template('main.html', flights_info=sorted(list(flights_info)), \
            avail_tickets=avail_tickets, avail_stay=sorted(list(stay_info)))

    flight_no = 'flight_no' in flask.request.form \
        and flask.request.form['flight_no']
    checkin_date = 'checkin_date' in flask.request.form \
        and flask.request.form['checkin_date']
    email_id = 'email_id' in flask.request.form \
        and flask.request.form['email_id']

    order_id = email_id +'_'+dt.now().isoformat()
    cond = {'flight': flight_no, 'stay': checkin_date}
    rollback_factor = random.random()

    with pymongo.MongoClient(mongo_url) as mcl:
        coll = mcl[cnst.mongo_db][cnst.mongo_coll]
        res = coll.find_one(cond)
        if not res:
            return 'No available package for your reservation'
        # quota_decr = {'$inc': {'quota': -1}}
        # quota_incr = {'$inc': {'quota': 1}}
        new_order = {'id': res['id'], 'email_id': email_id, 'order_id': order_id}
        # new_order = {'$push': {order_id: email_id}}
        if res['quota'] > 0:
            pass
            # _ = coll.update_one(cond, quota_decr)
        else:
            return {'QuotaError': 'No more quota'}
        #
        if rollback_factor >= 0.5:
            # reserving failure
            # _ = coll.update_one(cond, quota_incr)
            return {'OrderError': 'Order reservation failed'}
        else:
            # add reserve info into db
            if not coll.find_one({'id': new_order['id'], 'email_id': new_order['email_id']}):
                redis_pool = redis.ConnectionPool(host='localhost', port= 6379)
                with redis.Redis(connection_pool = redis_pool) as redis_conn: 
                    redis_conn.lpush('queue', json.dumps(new_order))
                    logging.info("Put a reservation to queue")
                # _ = coll.insert_one(new_order)
            else:
                # duplicate order, simply reject
                # _ = coll.update_one(cond, quota_incr)
                return 'OrderError: You had made a reservation'
    return "Reservation received, please wait for a while and check on /query your reservation"

@app.route("/query", methods=["GET", "POST"])
def query():
    mongo_url = f"""mongodb://{cnst.mongo_host}:{cnst.mongo_port}/"""

    if flask.request.method == 'GET':
        return render_template('booking_query.html')

    email_id = 'email_id' in flask.request.form \
        and flask.request.form['email_id']
    # res = []
    with pymongo.MongoClient(mongo_url) as mcl:
        cond = {'email_id': email_id}
        return redirect(url_for('query_email', email_id=cond['email_id']))
        '''
        coll = mcl[cnst.mongo_db][cnst.mongo_coll]
        tmp = coll.find(cond)
        for i in tmp:
            ori_id = i['id']
            info = coll.find_one({'id': ori_id, 'quota': {'$gt': -1}})
            res.append({'email_id': email_id, 'order_id': i['order_id'], \
                'stay': info['stay'], 'flight': info['flight'], 'price': info['price']})
    print(res)
    return render_template('booking_query_return.html', res=res)
    # return redirect(url_for('query_email'， email_id=cond['email_id']))
        '''

@app.route("/query/<email_id>", methods=["GET", "POST"])
def query_email(email_id):
    mongo_url = f"""mongodb://{cnst.mongo_host}:{cnst.mongo_port}/"""
    res = []
    with pymongo.MongoClient(mongo_url) as mcl:
        cond = {'email_id': email_id}
        coll = mcl[cnst.mongo_db][cnst.mongo_coll]
        tmp = coll.find(cond)
        for i in tmp:
            ori_id = i['id']
            info = coll.find_one({'id': ori_id, 'quota': {'$gt': -1}})
            res.append({'email_id': email_id, 'order_id': i['order_id'], \
                'stay': info['stay'], 'flight': info['flight'], 'price': info['price']})
    return render_template('booking_query_return.html', res=res)



if __name__ == '__main__':
    # q = Queue(maxsize=10)
    mongo_url = f"""mongodb://{cnst.mongo_host}:{cnst.mongo_port}/"""
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.DEBUG)
    # lock = threading.RLock()
    '''
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(consumer)
        executor.submit(app.run, \
            {'host':"0.0.0.0"},{'port':'8888'}, {'debug':True}, {'threaded':True})
    '''
    app.run(host="0.0.0.0", port=8888, debug=True, threaded=True)