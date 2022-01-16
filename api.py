from qgen import output
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def qgen():
    return "API IS WORKING"


@app.post("/qgen")
async def qgen(context : Request):
    req_info = await context.json()
    return output(req_info["urlId"],req_info["context"])