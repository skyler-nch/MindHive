import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pymongo import MongoClient
from pymongo import AsyncMongoClient
from dotenv import load_dotenv

from src.mongo_driver import caller
from src.structs import MongoRequest
"""
-skylers simple connection pool service-

a very simple connection pool service for mongodb

questions you might have:
1) why mongo?
for this particular task, where majority of the data is brought in by a web scraper,
it is better to use nosql because BASE fits our use case more than ACID. Mongo happens to also 
be among the fastest nosql databases that does not require advanced sharding setups

2) what about vector databases?
yes, it would be better, but the use case right now is too simple to justify setting up a vector database,
also mongo has a vector search function on their cloud platform, so it is easy to migrate

3) what about using ORMs 
not usable since we are using nosql

4) whats with the standalone functions to do CRUD in mongo_driver.py?
I normally prefer to write my own interfaces to libraries when it comes to interacting with dbs, helps me a with a few things:
-avoid overcomplicating queries, and balance computational cost between db engine and api service
-they are shared utils functions that can be used throughout the whole service to make it easier to code
-if there comes a time to migrate to other dbs, you just need to change the interface code

5) Doesn't a dedicated connection pool service defeat the purpose of a microservice architecture?
Yes

6) Why then?
ok there is a few nuances where this is acceptable, it is not ok to have one single unified connection pool service,
rather it should be each service that requires connection pooling should have its own connection pool service -or-
each cluster of logically seperated dbs having its own connection pool service. The problem now is that most companies
(that I've seen at least) has never scaled to a point where a justification for a seperate connection pool service, and it
is more convenient for them to just stuff the db interface into their services alone, with no technical drawbacks

-however-

having a seperate connection pool service despite not needing one has some logistical advantages:
-for sql databases, you can force transactions on (because some developers still don't use transactions)
-actual tamper proof logging system, where developers cant forget to log things
-logic code is physically seperate from the model, therefore the repository becomes ridiculously clean
-simpler to cache and invalidate cache for a large segment of the architecture, especially in a microservice/cluster environment
-again, switching dbs becomes a cakewalk
-better inter-service authorization 
-strict adherance to active connection limits per cluster of service

-with one downside:
using sqlalchemy defined structs is impossible

but i dont like sqlalchemy in general so it checks out, 
devs do have a tendency to squeeze all logic into an insanely complex query within sqlalchemy, which is not
great, besides the usual debate between using ORMs or raw sql.

personally, I still like the migrations tool by alembic(sqlalchemy) though, or even djangos migration,
but I have been using more nosqls than sqls lately and haven't gotten around to look for migration alternatives

currently since there is only one db with very few functionalities, architecture wise it is still fine
optimally, there shouldnt be a connection pool service because its an additional point of failure
but starting a project with it motivates people to not be monolithic in their code and provides alot of 
logistical benefit that improves development velocity immensely
but should more features be added, then this cannot be the only connection pool service available
if using postgres, instead of coding up another connection pooling service, just use pgbouncer, im not sure about others
"""
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR,'.env'))

app = FastAPI()

origins = [
    "http://172.18.0.1:5002",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def connect_to_mongo():
    client = MongoClient(os.getenv("MONGO_CONN_STRING"))
    return client

MONGOCLIENT = connect_to_mongo()

@app.post("/mongo")
async def mongo(payload:MongoRequest):
    response = caller(MONGOCLIENT,**payload.model_dump())
    return response

@app.get("/")
async def root():
    return {"message": "Hello World","detail":"connection-pool"}
