import os
from dotenv import load_dotenv
from fastapi import FastAPI
import time

from src.spider_caller import run_spider

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR,'.env'))

"""
-skylers overengineered scraping tool-
the goal is to have this service be able to have a spider running on request
mainly because you could have a CRON service be able to call the spider in order to update data
but scrapy uses twisted reactor that cannot be restarted, therefore we need to overcomplicate some things...

this service has two concepts: 
1) standalone scrapy spider scripts
2) fastapi server that uses celery to manage subprocesses for calling spiders

downside is that:
you need to pipe out the output of the spider to a file and re-read it via another process to the db 
though you can simply push to db in the spider, but each request will become expensive, and you can't seperate the task

but since the purpose of this service is to only allow a scheduling service to call on this api(IRL this service should only run once a month i guess)
pushing to db in the spider is not of consequence

requires redisdb as a broker for celery

no pydantic on fastapi layers because there will only be one struct, and will be pointless
"""

app = FastAPI()


@app.get("/scrape")
async def scrape():
    spider_name = "sandwich_spider" #for convenience sake ill hard-code the spider_name
    run_spider(spider_name)
    return {"detail":"success"} 


@app.get("/")
async def root():
    return {"message": "Hello World, this is the scraping service"}