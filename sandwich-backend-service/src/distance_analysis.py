from vincenty import vincenty
from itertools  import combinations
from typing import Generator

from src.structs import MongoPayloadStruct, StoreContentStruct, TwoStoresDistanceStruct
from src.request import mongo_request


"""
Vincenty is far more accurate to calculate the distance between two coordinates
compared to Haversine, where it has the accuracy of up to >1mm, however Vincenty 
cannot calculate two points that are nearly antipodal (a pair of coordinates that are opposite side of the earth)
Since we are just calculating points within malaysia, this is usable

>isn't it better to have front end do this calculation?
well front end methodology (without geospatial libraries) is to calculate 
intersecting circles by pixels,which is arguably more inaccurate, 
with geospatial libraries(turfjs), they use the same formula(I might be wrong). 
However considering that it is (~300 stores * ~300 stores) that the client has to calculate every single time
and that the stores do not pop up every second, its better for backend to calculate it and 
save the results.
"""

def get_intersecting(min_distance:int):
    payload = MongoPayloadStruct(
        collection="SandwichStoresDistance",
        operation="find_all",
        data={"distance":{"$lte":min_distance}}
    )
    response:list[dict] = mongo_request(payload).json()

    shop_set:set = set()
    for item in response:
        shop_set.add(item["shop_1"]) # TODO: should add to a struct for validation
        shop_set.add(item["shop_2"]) # TODO: should add to a struct for validation
    print(len(shop_set))
    return list(shop_set)

def generate_distances():
    payload = MongoPayloadStruct(
        collection="SandwichStores",
        operation="find_all",
        data={}
    )
    response:list[dict] = mongo_request(payload).json()

    shops:dict[StoreContentStruct] = dict()

    for item in response:
        item["id"] = item["_id"] #because pydantic cannot accept fields with _ as a prefix
        shops[item["_id"]] = StoreContentStruct(**item)
    
    ids:list[int] = list(shops.keys())
    combination:Generator[tuple[int],None,None] = combinations(ids,2) #generator for all combination of id pairs

    result = []
    for combine in combination:
        shop_1_id:int = combine[0]
        shop_2_id:int = combine[1]

        shop_1_coords:tuple = (shops[shop_1_id].latitude,shops[shop_1_id].longitude)
        shop_2_coords:tuple = (shops[shop_2_id].latitude,shops[shop_2_id].longitude)

        two_stores_distance = TwoStoresDistanceStruct(
            id = str(combine),
            shop_1=shop_1_id,
            shop_2=shop_2_id,
            distance=vincenty(shop_1_coords,shop_2_coords)

        )
        result.append(two_stores_distance.model_dump(by_alias=True))
    
    publishing_payload = MongoPayloadStruct(
        collection="SandwichStoresDistance",
        operation="batch_usert_insert",
        data=result
    )
    response = mongo_request(publishing_payload).json()
    return response