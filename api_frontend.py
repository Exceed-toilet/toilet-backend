from pymongo import MongoClient

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import datetime

client = MongoClient('mongodb://localhost', 27017)

db = client["toilet_project"]

collection1 = db["enter"]
collection2 = db["exit"]

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        print(toilet)
        query = {
            "room_num": toilet.room_num,
            "use_status": toilet.use_status,
            "exit": datetime.datetime.now()
        }
        collection2.insert_one(query)
        return {
            "result": "OK"
        }
    elif toilet.use_status == 1:
        query = {
            "room_num": toilet.room_num,
            "use_status": toilet.use_status,
            "enter": datetime.datetime.now()
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


@app.get('/toilet/time-estimated/{room_num}')
def get_estimated(room_num: int):
    list_delta_time = []
    list_result = list(collection1.find({"room_num": room_num}, {"_id": 0}))
    size = len(list(collection2.find({"room_num": room_num}, {"_id": 0})))
    for i in range(size-1):
        for j in range(size-1):
            if len(list_result) != 0 and len(list(collection2.find({"room_num": room_num}, {"_id": 0}))) != 0:
                if list(collection2.find({"room_num": room_num}, {"_id": 0}))[i]["exit"] > list_result[j]["enter"]:
                    delta = (list(collection2.find({"room_num": room_num}, {"_id": 0}))[i]["exit"]
                              - list_result[j]["enter"])
                    second = delta/datetime.timedelta(seconds=1)
                    list_delta_time.append(second)
    estimated_time = sum(list_delta_time) / len(list_delta_time)
    estimated_min = estimated_time/60
    estimated_second = estimated_time - (int(estimated_min)*60)
    string_estimated = f"{int(estimated_min)} min:{estimated_second:.2f} second"
    if len(list_result) == 0 and len(list(collection2.find({"room_num": room_num}, {"_id": 0}))) == 0:
        return {
            "result": "FAIL"
        }
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


@app.get('/toilet/how-long/by-room/{room_num}')
def check_long_use(room_num: int):
    list_result = list(collection1.find({"room_num": room_num}, {"_id": 0}))
    if len(list_result) != 0 and len(list(collection2.find({"room_num": room_num}, {"_id": 0}))) != 0:
        if list(collection2.find({"room_num": room_num}, {"_id": 0}))[-1]["exit"] < list_result[-1]["enter"]:
            minute = (datetime.datetime.now() - list_result[-1]["enter"]).total_seconds() / 60
            second = (datetime.datetime.now() - list_result[-1]["enter"]).total_seconds() - int(minute) * 60
            return {
                "result": f"{int(minute)} min: {second:.2f} sec"
            }
        else:
            return {
                "result": "FAIL"
            }
    elif len(list_result) != 0 and len(list(collection2.find({"room_num": room_num}, {"_id": 0}))) == 0:
        minute = (datetime.datetime.now() - list_result[-1]["enter"]).total_seconds()/60
        second = (datetime.datetime.now() - list_result[-1]["enter"]).total_seconds() - int(minute)*60
        return {
            "result": f"{int(minute)} min: {second:.2f} sec"
        }
    return {
        "result": "FAIL"
    }
