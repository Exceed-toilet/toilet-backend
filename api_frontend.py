from pymongo import MongoClient

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.encoders import jsonable_encoder


client = MongoClient('mongodb://localhost', 27017)

db = client["toilet_project"]

collection = db["user"]

app = FastAPI()
