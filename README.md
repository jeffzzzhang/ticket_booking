# ticket_booking
This is a ticket booking project for the promotion campaign of some hotel. Finished in early Sep 2022.

Some luxury hotel is going to launch a campaign online which sells packages including a flight and 1-day accommodation at a very low price.  Here is an example of the packages in JSON:  {   "packages": [{ "id": 1, "flight": "Flight-1", "stay": "2022-08-09", "price": 100, quota: 1 },     { "id": 2, "flight": "Flight-2", "stay": "2022-08-09", "price": 100, quota: 2 },     { "id": 3, "flight": "Flight-3", "stay": "2022-08-10", "price": 100, quota: 2 }, { "id": 4, "flight": "Flight-3", "stay": "2022-08-11", "price": 100, quota: 2 }   ] } Frontend Please implement the following features in frontend  a page to place select pacakges and place an order with an email a result page that shows the order with details, or simply a fail message a page to show an order by order ID with the email used when purchase the order Backend Please implement the following features in backend  an endpoint to reserve flight Please fail 50% of the reservation randomly an endpoint to reserve a hotel room a valid flight ticket number MUST be provided in order to make the reservation an endpoint to purchase a package only allow to purchase package with quota > 0, if quota runs out, throw an exception consume 1 quota before reserving flight and hotel room as to avoid oversale release the quota (add back 1) once either flight or hotel room reservation fail an endpoint to retrieve the order by ID and email Design and explanations.

# Tech Selection
This is a full-stack project, from UI, to ticket booking in middle, and data storage to a specific database. Here's the explaination of tech selection.

## Frontend
Minimal UI is used to implement ticket booking, i.e., static HTML. 

Order page: as users open order page, backend will return available quotas. User select desirable flight and stay date, before submitting to backend.

Query page: the orders and related info can be queryed by user email on the query page.

## Booking
Booking is the tricky part of this project. Users send requests via UI, and booking part simply checks quota availablity and makes a reservation. The hidden problem is that multi-users may send requests simultaneously, which leads to the infamous Race-condition and brings chaos to database. In the part, I took **Lock/Mutex** mechanism to deal with it. Once a request comes in, it acquires a lock to update backend db. Before the lock is released, other requests are blocked and unable to make a reservation/update database. They have to wait before lock released. In this synchronisation way, race-condition can be avoided.

An alternative is to push incoming requests into a message queue, and a running threading process messages in the queue in a constant way.

## Database
The mix of flight and stay makes reseavation info quite complicated. For example, for each specific flight, available stays may differ from each other. And given different status of each package, it may be more complex. I chose mongoDB as the database, cause it is easy and flexible to update reservation info based on package id. 

Each package holds a unique id, which is `id` in mongo collection `hotel`. Originally, package is a record of (`id`, `flight`, `stay`, `quota`). Once user makes a successful reservation, a new record is generated as (`id`, `email_id`, `order_id`). So the field `id` combines order info and package info in mongoDB.

## Web Framework
In the project, the business is relatively simple and straightward. So I choose a light-weighted framework Flask as the web framework. Compared with widely-used Django, Flask facilitates developers with easy usage.  And WSGI framework is pending for now. If workload is increasing, Gunicorn tool can be applied in production env.

## Container
Docker is chosen as the container. With the help of docker container, no virtual env is required to run the project, which is time-consuming in operation and resource-consuming. Besides, Python dependency can be installed in an efficient way.

# Manual
## Data Initialisation
Once images are launched, data initialisation as follows is required to insert original packages to database.
```
python db_init.py
```
## API
url localhost:8888

* GET /order make a reservation on the page

* GET /query if reservation is completed, check booking on the page

## Files
* app.py: main scripts and entry function
* constant.py: some frequently-used constants
* db_init.py: for data initialisation

# Plan B - Queue
Lock mechanism is chosen as the method to guarantee synchronisation. I also use producer-consumer pattern for sync. 

Requests are sent to Redis list with `lpush` at producer side. And consumer fetches the requests from Redis list with `rpop`. No lock needed for db update, cause consumer only deals with a request each time.

Simply launch producer/Flask with `python app_queue.py` and launch consumer with `python queue_consumer.py` in another process.

## API
url localhost:8888

* GET /order-queue make a reservation on the page

## Files
* app_queue.py: main scripts in producer-consumer mode
* queue_consumer.py: consumer side of producer-consuer mode, fetching one element from queue and update into mongoDB

