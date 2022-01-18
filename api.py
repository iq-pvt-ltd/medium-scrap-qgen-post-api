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
    scrapContent = scrap(req_info["inputLink"])
    print("Scrapped")
    return output(req_info['urlId'],scrapContent["Content"])