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

list_enter_timestamp = []
list_exit_timestamp = []
list_delta_time = []


class Toilet(BaseModel):
    room_num: int
    use_status: int


@app.post('/toilet')
def post_hardware(toilet: Toilet):
    """
    use_status = 0 is no user
    use_status = 1 is no user
    """
    if toilet.use_status == 0:
        list_exit_timestamp.append({str(toilet.room_num): datetime.now()})
        return {
            "result": "OK"
        }
    elif toilet.use_status == 1:
        list_enter_timestamp.append({str(toilet.room_num): datetime.now()})
        return {
            "result": "OK"
        }
    return {
        "result": "FAIL"
    }


@app.get('/toilet/by-room/{room_num}')
def get_toilet(room_num: int):
    list_result = list(collection.find({"room_number": room_num}, {"_id": 0}))
    if len(list_result) != 0:
        data = []
        for result in list_result:
            data.append(result)
        return data
    else:
        raise HTTPException(404, f"Couldn't find toilet with room number: {room_num}'")


@app.get('/toilet/time-estimated')
def get_estimated():
    estimated_time = sum(list_delta_time) / len(list_delta_time)
    query = {
        "average_time": estimated_time
    }
    return query


@app.get('/toilet/enter-time/by-room/{room_num}')
def get_enter(room_num: int):
    for i in range(len(list_enter_timestamp), 0, -1):
        room = list(list_enter_timestamp[i].keys())[0]
        if room == room_num:
            return {
                "result": list_enter_timestamp[i]["room_num"]
            }
        else:
            return {
                "result": "FAIL"
            }


@app.get('/toilet/enter-time/by-room/{room_num}')
def get_exit(room_num: int):
    for i in range(len(list_exit_timestamp), 0, -1):
        room = list(list_exit_timestamp[i].keys())[0]
        if room == room_num:
            return {
                "result": list_exit_timestamp[i]["room_num"]
            }
        else:
            return {
                "result": "FAIL"
            }


def delta_time():
    list_delta = []

    for i in range(len(list_exit_timestamp)):
        delta = list_enter_timestamp[i]["room_num"]-list_enter_timestamp[i]["room_num"]

    re