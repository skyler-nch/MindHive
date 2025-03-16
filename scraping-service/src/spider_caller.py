from celery.app import Celery
import os
import subprocess
from fastapi.exceptions import HTTPException

redis_url = os.getenv("REDIS_URL")

celery_app = Celery(
    "scraper",
    broker = redis_url,
    backend = redis_url
)

#celery task to invoke a subprocess that calls the spider script file
#this way its technically still asynchronous while bypassing the twisted reactor limitation
@celery_app.task
def run_spider(spider_name):
    #command to call the spider script
    command = ["python", f"src/scrapy_spiders/{spider_name}.py"]

    #call subprocess on the command and collect the stdout/stderror 
    process = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    #blocking call that runs the process, but since its a subprocess its in an external thread from the main event loop
    stdout, stderr = process.communicate()

    #checks if the process succeeded
    if process.returncode != 0:
        raise HTTPException(500,f"Error: {stderr.decode('utf-8')}")
    else:
        print(f"Sandwich Spider found some stores!!!")