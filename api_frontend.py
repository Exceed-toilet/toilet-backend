from pymongo import MongoClient

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.encoders import jsonable_encoder
from datetime import datetime


client = MongoClient('mongodb://localhost', 27017)

db = client["toilet_project"]

collection1 = db["enter"]
collection2 = db["exit"]

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
    use_status = 0 don't has user
    use_status = 1 has user
    """
    if toilet.use_status == 0:
        print(str(toilet.room_num) + f"{datetime.now()}")
        query = {
            "room_num": toilet.room_num,
            "use_status": toilet.use_status,
            "exit": datetime.now()
        }
        collection2.insert_one(query)
        return {
            "result": "OK"
        }
    elif toilet.use_status == 1:
        query = {
            "room_num": toilet.room_num,
            "use_status": toilet.use_status,
            "enter": datetime.now()
        }
        collection1.insert_one(query)
        return {
            "result": "OK"
        }
    return {
        "result": "FAIL"
    }


@app.get('/toilet/by-room/{room_num}')
def get_toilet(room_num: int):
    list_result = list(collection1.find({"room_num": room_num}, {"_id": 0}))
    if list(collection2.find({"room_num": room_num}, {"_id": 0}))[-1]["exit"] < list_result[-1]["enter"]:
        if len(list_result) != 0:
            data = []
            for result in list_result:
                data.append(result)
            return data[-1]
        else:
            raise HTTPException(404, f"Couldn't find toilet with room number: {room_num}'")


def delta_time():
    list_delta = []
    for i in range(len(list_exit_timestamp), 0, -1):
        for j in range(len(list_exit_timestamp), 0, -1):
            if list(list_enter_timestamp[i].keys())[0] == list(list_exit_timestamp[j].keys())[0]:
                if list_enter_timestamp[i]["room_num"] < list_exit_timestamp[j]["room_num"]:
                    delta = list_exit_timestamp[j]["room_num"] - list_enter_timestamp[i]["room_num"]
                    second = delta.total_second()
                    list_delta.append(second)
    return list_delta


@app.get('/toilet/time-estimated')
def get_estimated():
    list_delta_time = delta_time()
    estimated_time = sum(list_delta_time) / len(list_delta_time)
    estimated_min = estimated_time/60
    estimated_second = estimated_time - (int(estimated_min)*60)
    string_estimated = f"{int(estimated_min)} min:{estimated_second} second"
    query = {
        "average_time": string_estimated
    }
    return query


@app.get('/toilet/enter-time/by-room/{room_num}')
def get_enter_time(room_num: int):
    list_result = list(collection1.find({"room_num": room_num}, {"_id": 0}))
    if len(list_result) != 0:
        return {
                "result": list_result[-1]["enter"]
            }
    else:
        return {
            "result": "FAIL"
        }


@app.get('/toilet/exit-time/by-room/{room_num}')
def get_exit_time(room_num: int):
    list_result = list(collection2.find({"room_num": room_num}, {"_id": 0}))
    if len(list_result) != 0:
        return {
            "result": list_result[-1]["exit"]
        }
    else:
        return {
            "result": "FAIL"
        }


