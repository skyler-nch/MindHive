from pydantic import BaseModel,Field

class MongoPayloadStruct(BaseModel):
    db:str = "MindHive"
    collection:str
    operation: str
    data: dict | list[dict]

class StoreContentStruct(BaseModel):
    id:int = Field(serialization_alias="_id")
    name:str = None
    address:str = None
    google_map_link:str = None
    waze_link:str = None
    opening_times:list = None
    latitude:float = None
    longitude:float = None

class RAGDocumentStruct(BaseModel):
    id:int
    name:str
    text:str