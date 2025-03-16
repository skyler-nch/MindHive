import os
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import RedirectResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests


from src.router import routes
from src.structs import AddPathStruct, PathDetailStruct, PathStruct, RetrievePathStruct


BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

app = FastAPI()
Route = routes()


origins = [

]

@app.get("/")
def root():
    return {"message":"Hello World", "detail":"api-gateway"}

@app.get("/{pathinput}")
async def route(pathinput: str, request: Request):
    path = PathStruct(id=pathinput)
    query = request.query_params
    redirect_link = Route.retrieve_route(path)
    if redirect_link == None:
        raise HTTPException(status_code=404, detail="path does not exist (api-gateway)")
    url = redirect_link["link"]+f"?{query}"
    return RedirectResponse(url)

@app.post("/{pathinput}")
async def route(pathinput:str, request: Request):
    path = PathStruct(id=pathinput)
    redirect_link = Route.retrieve_route(path)
    if redirect_link == None:
        raise HTTPException(status_code=404, detail="path does not exist (api-gateway)")
    header = {'Location':redirect_link["link"]}
    payload = await request.body()
    print(payload)
    return Response(headers=header, content=payload, status_code=status.HTTP_307_TEMPORARY_REDIRECT)