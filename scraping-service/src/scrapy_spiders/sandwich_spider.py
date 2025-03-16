import scrapy
import json
from json import JSONDecodeError

from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.signalmanager import dispatcher
from pydantic import BaseModel

from sandwich_structs import StoreContentStruct,StoreSchemaStruct, MongoPayloadStruct

import requests
import os

"""
The website has no need for pagination, nor filters, coordinates are also already freely given
The website simply loads in every single subway store via a script, filtering locally

The sandwich spider simply scrapes for the store data within its script file of the website and parses it to a dict
"""
class SandwichSpider(scrapy.Spider):
    name:str = "sandwich"

    def start_requests(self):
        url:str = "https://subway.com.my/find-a-subway"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response)->list[dict]:
        #xpath that checks for script tags with no sources, and with the js containing canvasId = fp_google_map
        response:str =  response.xpath('//script[not(@src) and contains(text(),"fp_googleMap")]').get()

        #within the current context, regex is less efficient than slicing by index
        try:
            start_anchor:str = "map.init("
            ending_anchor:str = "$.sloc.map.register('1', map);"

            start_index:int = response.index(start_anchor) + len(start_anchor) #searches left to right, and starting index added by its own length of query
            ending_index:int = response.rindex(ending_anchor) #searches right to left

            json_string:str = response[start_index:ending_index].strip()[:-2] #strips whitespace, and removes trailing syntax ");"

            json_response:dict = json.loads(json_string) #converts the raw string to dict

            marker_data:list = json_response["markerData"] #removes unnecessary keys

        except ValueError as e:
            raise ValueError("Website has changed, please update xpath and json extraction",e)
        except JSONDecodeError as e:
            raise JSONDecodeError("json response has encountered an error, please update spider",e)
        except KeyError as e:
            raise KeyError("json response missing markerData, please review spider response",e)

        f = open("text.json","w")
        f.write(str(marker_data))
        f.close()

        return marker_data





def parse_content(html_string:str) -> StoreContentStruct:
    selector = Selector(text=html_string)

    name:str = selector.xpath("//h4/text()").get()

    #generally the first p tag is the address, with subsequent ones the opening hours
    #the last p tag will always be empty
    content:list[str] = selector.xpath("//div[contains(@class,'infoboxcontent')]/p/text()").getall()

    #there are some shops with multiple opening hour paragraphs, list is required
    time:list[str] = []
    address:str = ""
    for i in range(len(content)-1):
        if i == 0:
            address:str = content[0]
        else:
            time += [content[i]]

    map_links:list[str] = selector.xpath("//div[contains(@class,'directionButton')]/a/@href").getall()
    google_map_link:str = map_links[0]
    waze_link:str = map_links[1]

    return StoreContentStruct(
        name=name,
        address=address,
        google_map_link=google_map_link,
        waze_link=waze_link,
        opening_times=time,
    )
    ...

#convert marker_data into schema for database input
#validates via pydantic
def to_schema(marker_data:list[dict]) -> list[dict]:
    response = []
    for store in marker_data:
        store_content = parse_content(store["infoBox"]["content"])
        
        s = StoreSchemaStruct(
            id = int(store["id"]),
            latitude = float(store["position"]["lat"]),
            longitude = float(store["position"]["lng"]),
            **store_content.model_dump()        
        )
        response.append(s.model_dump())
    

    return response

def publish(data):
    basedbpath = os.getenv("CONNECTIONPOOLPATH") + "/mongo"
    payload = MongoPayloadStruct(
        operation="batch_usert_insert",
        data=data
    )
    response = requests.post(basedbpath,json=payload.model_dump(by_alias=True))
    return response

def sandwich_spider_caller() -> int:
    results = []

    #internal function to get results for marker_data
    def crawler_results(signal, sender, item, response, spider):
        results.append(item)
    
    #connects to the signal and callbacks to the internal function
    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    process = CrawlerProcess()
    process.crawl(SandwichSpider)
    process.start()

    try:
        data = to_schema(results)
    except Exception as e:
        raise TypeError("Cannot cast to schema", e)
    
    response = publish(data)

    return 1

if __name__ == "__main__":
    sandwich_spider_caller()