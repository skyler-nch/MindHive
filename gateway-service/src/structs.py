from pydantic import BaseModel, Field


class PayloadStruct(BaseModel):
    payload:dict = None

class PathStruct(BaseModel):
    id:str = Field(serialization_alias="_id")

class PathDetailStruct(BaseModel):
    id:str = Field(serialization_alias="_id")
    link:str
    method:str

class MongoRequestStruct(BaseModel):
    db: str
    collection: str
    operation: str

class AddPathStruct(MongoRequestStruct):
    data: PathDetailStruct

class RetrievePathStruct(MongoRequestStruct):
    data: PathStruct