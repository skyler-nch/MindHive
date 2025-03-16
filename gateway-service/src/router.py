import os
import requests

from src.structs import AddPathStruct, PathDetailStruct, PathStruct, RetrievePathStruct

class routes:
    def __init__(self):
        self.basedbpath = os.getenv("CONNECTIONPOOLPATH") + "/mongo"
        print(self.basedbpath)

    def _postrequest(self,payload:dict):
        response = requests.post(self.basedbpath,json=payload)
        return response.json()

    def retrieve_route(self,pathdata:PathStruct):
        payload = RetrievePathStruct(
            db = "MindHive",
            collection = "Routes",
            operation = "find_one",
            data = pathdata
        )
        return self._postrequest(payload.model_dump(by_alias=True))

    def create_route(self,pathdata:PathDetailStruct):
        payload = AddPathStruct(
            db = "MindHive",
            collection = "Routes",
            operation = "insert_one",
            data = pathdata
        )
        return self._postrequest(payload.model_dump(by_alias=True))
    
