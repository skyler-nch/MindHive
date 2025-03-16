import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from dotenv import load_dotenv

from src.qwen_interface import Qwen

#TODO: overall type hintings, documention

BASEDIR  = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR,".env"))

models = dict()

origins = [

]

@asynccontextmanager
async def lifespan(app:FastAPI):
    #this will reinitialise after every reset, including filesaves
    #TODO: move this to a main caller
    models.update({"qwen":Qwen()})
    yield
    models.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message":"Hello World","detail":"I am Qwen! specifically tweaked to talk about subway stores"}

@app.get("/query")
def query(query:str):
    response = models["qwen"].generate(query)
    return {"response":response}


