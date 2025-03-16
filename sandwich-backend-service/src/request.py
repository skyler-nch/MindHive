import requests
from src.structs import MongoPayloadStruct

#TODO: a generalised request function would be lovely
def mongo_request(payload:MongoPayloadStruct):
    response = requests.post("http://172.21.0.1:3000/mongo",json=payload.model_dump())
    return response