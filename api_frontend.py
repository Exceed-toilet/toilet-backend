from pymongo import MongoClient

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.encoders import jsonable_encoder
from datetime import datetime


client = MongoClient('mongodb://localhost', 27017)

db = client["toilet_project"]

collection = db["user"]

app = FastAPI()

list_timestamp = []

list_estimated = []


class Toilet(BaseModel):
    room_num: int
    use_status: int


@app.post('/toilet')
def post_hardware(toilet: Toilet):
    """"""
    if toilet.use_status == 0:
        list_timestamp.append(datetime.now())
        return {
            "result": "OK"
        }
    elif toilet.use_status == 1:
        list_timestamp.append(datetime.now())
        return {
            "result": "OK"
        }
    return {
        "result": "FAIL"
    }
