from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Measure(BaseModel):
    sensor: str
    value: float


@app.get("/")
def home():
    return {"message": "SensorOps API running"}


@app.post("/measure")

def receive(data: Measure):

    return{"received": data.model_dump()}



