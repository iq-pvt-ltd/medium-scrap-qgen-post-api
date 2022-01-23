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
    print(req_info)
    print(req_info['message'])
    print(req_info['message']['attributes'])
    print(req_info['message']['attributes']['inputLink'])
    scrapContent = scrap(req_info['message']['attributes']['inputLink'])
    print(".......Scrapped.......")
    return output(req_info['message']['attributes']['urlId'],scrapContent["Content"])