import requests

def _get_dict_parser(query:dict) -> str:
    output_query = ""
    for k,v in query.items():
        output_query += f"{k}={v}&"
    return output_query


#there should be a prettier way to write all this im just tired now
def get_request(subpath:str,args:dict = {}): 
    response = requests.get(f"http://127.0.0.1:3000{subpath}?{_get_dict_parser(args)}")
    return response.json()

def post_request(subpath:str,args:dict = {}):
    response = requests.post(f"http://127.0.0.1:3000{subpath}",json=args)
    return response.json()