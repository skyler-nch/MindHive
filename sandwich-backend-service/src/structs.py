from pydantic import BaseModel, Field

class MongoPayloadStruct(BaseModel):
    db:str = "MindHive"
    collection:str
    operation: str
    data: dict | list[dict]

class CoordinateStruct(BaseModel):
    id:int
    latitude:float
    longitude:float

class StoreContentStruct(BaseModel):
    id:int = Field(serialization_alias="_id")
    name:str = None
    address:str = None
    google_map_link:str = None
    waze_link:str = None
    opening_times:list = None
    latitude:float = None
    longitude:float = None

class TwoStoresDistanceStruct(BaseModel):
    id:str = Field(serialization_alias="_id")
    shop_1:int
    shop_2:int
    distance:float
