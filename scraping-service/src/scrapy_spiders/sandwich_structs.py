from pydantic import BaseModel,Field

class StoreContentStruct(BaseModel):
    name:str = None
    address:str = None
    google_map_link:str = None
    waze_link:str = None
    opening_times:list = None
    
class StoreSchemaStruct(StoreContentStruct):
    id:int = Field(serialization_alias="_id")
    latitude:float = None
    longitude:float = None

class MongoPayloadStruct(BaseModel):
    db:str = "MindHive"
    collection:str = "SandwichStores"
    operation: str
    data: list[StoreSchemaStruct]