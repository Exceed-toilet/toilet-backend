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


@app.get('/toilet/time-estimated')
def get_estimated():
    list_delta_time = []
    for i in list(collection1.find({})):
        for j in list(collection2.find({})):
            delta = j["exit"] - i["enter"]
            total_second = delta
            list_delta_time.append(total_second)
    estimated_time = sum(list_delta_time) / len(list_delta_time)
    estimated_min = estimated_time/60
    estimated_second = estimated_time - (int(estimated_min)*60)
    string_estimated = f"{int(estimated_min)} min:{estimated_second} second"
    query = {
        "average_time": list_delta_time
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


@app.get('/toilet/how-long/by-room/{room_num}')
def check_long_use(room_num: int):
    list_result = list(collection1.find({"room_num": room_num}, {"_id": 0}))
    if len(list_result) != 0 and len(list(collection2.find({"room_num": room_num}, {"_id": 0}))) != 0:
        if list(collection2.find({"room_num": room_num}, {"_id": 0}))[-1]["exit"] < list_result[-1]["enter"]:
            return {
                "result": (datetime.now() - list_result[-1]["enter"])
            }
        else:
            return {
                "result": "FAIL"
            }
    elif len(list_result) != 0 and len(list(collection2.find({"room_num": room_num}, {"_id": 0}))) == 0:
        minute = (datetime.now() - list_result[-1]["enter"]).total_seconds()/60
        second = (datetime.now() - list_result[-1]["enter"]).total_seconds() - int(minute)*60
        return {
            "result": f"{int(minute)} min: {second:.2f} sec"
        }
    return {
        "result": "FAIL"
    }
