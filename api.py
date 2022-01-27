import os
from qgen import output
from scrapper import scrap
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def qgen():
    return "API IS WORKING"


@app.post("/qgen")
async def qgen(context : Request):
    req_info = await context.json()
    print(".......req_info.......")
    print(os.getenv('CLOUD_TRIGGER_URL'))
    print(os.getenv('SELENIUM_URL'))
    scrapContent = scrap(req_info['message']['attributes']['inputLink'],req_info['message']['attributes']['urlId'])
    print(".......Scrapped.......")
    if scrapContent == None or len(scrapContent["Content"])==0:
        print(".....Exiting.....")
        return {"Message":"Unable to Generate Question"}
    else:
        return output(req_info['message']['attributes']['urlId'],scrapContent["Content"])