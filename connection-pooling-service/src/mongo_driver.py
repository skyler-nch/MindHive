from pymongo import MongoClient, ReplaceOne
from pymongo.errors import DuplicateKeyError
from fastapi.exceptions import HTTPException

def _find_one(collection:MongoClient, data:dict):
    response = collection.find_one(data)
    return response

def _find_all(collection:MongoClient, data:dict):
    response = list(collection.find(data))
    return response

def _insert_one(collection:MongoClient, data:dict):
    id = collection.insert_one(data)
    return {"inserted_id":str(id.inserted_id)}

def _text_search(collection:MongoClient, data:dict):
    #expects the data to be {"query":text-to-be-searched}
    #no substring search for now, need to use regex if we want substring search
    response =  list(collection.find({"$text":{"$search":data["query"]}}))
    return response

#conditionless insert, replacing those that _id already exists
def _batch_usert_insert(collection:MongoClient, data:list[dict]):
    requests = []
    for item in data:
        requests.append(ReplaceOne({"_id":item["_id"]},item,upsert=True))
    collection.bulk_write(requests)
    
    # id = collection.insert_one(data)
    # return {"inserted_id":str(id.inserted_id)}

functions = {"find_one":_find_one,
             "find_all":_find_all,
             "insert_one":_insert_one,
             "batch_usert_insert":_batch_usert_insert,
             "text_search":_text_search,
             }

def caller(client:MongoClient, db:str, collection:str,operation:str, data:dict):
    try:
        print(collection,operation,data)
        collection = client[db][collection]
        response = functions[operation](collection, data)
        return response
    except DuplicateKeyError:
        return HTTPException(400,"duplicate key error")
    except KeyError:
        return HTTPException(405,"operation does not exist")
    except:
        return HTTPException(400,"unknown error")

