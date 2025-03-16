import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

from src.structs import MongoPayloadStruct
from src.request import mongo_request
from src.distance_analysis import generate_distances, get_intersecting

BASEDIR  = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR,".env"))

app = FastAPI()

origins = [

]

@app.get("/")
def root():
    return {"message":"Hello World","detail":"sandwich-backend-service"}

@app.get("/getshops")
def get_shops(id:int = None):
    payload = MongoPayloadStruct(
        collection="SandwichStores",
        operation="find_all",
        data={"_id":id} if id != None else {} #TODO: swagger typehinting fails because of this, use proper structs when time allows
    )
    response = mongo_request(payload)
    return response.json()

@app.get("/queryshops")
def query_shops(query:str):
    #TODO: bug where Kuala lumpur will return all cities that has Kuala *
    payload = MongoPayloadStruct(
        collection="SandwichStores",
        operation="text_search",
        data={"query":query}
    )
    response = mongo_request(payload)
    return response.json()

@app.get("/generateintersectingshops")
def generateintersectingshops():
    response = generate_distances()
    return response

@app.get("/getintersectingshops")
def get_intersecting_shops(distance:int):
    response = get_intersecting(distance)
    return response