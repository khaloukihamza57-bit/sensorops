import os
from contextlib import asynccontextmanager


import psycopg 
from psycopg.rows import dict_row
from fastapi import FastAPI, Query
from pydantic import BaseModel



def get_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        row_factory=dict_row
    )
@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT  EXISTS measurements (
                id SERIAL PRIMARY KEY,
                sensor TEXT NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                create_at TIMESTAMPTZ DEFAULT NOW()
            )
       """)
    yield
app = FastAPI(lifespan=lifespan)



class measure(BaseModel):
    sensor: str
    value: float


@app.get("/")
def home():
    return{"message": "SensOrops API running"}
@app.post("/measure",status_code=201)
def receive(data: measure):
    with get_connection() as conn:
         result = conn.execute(
             """
             INSERT INTO measurements (sensor, value)
             VALUES (%s, %s)
             RETURNING id, sensor, value, created_at
             """,
            (data.sensor,data.value),
         ).fetchone()
    return result


@app.get("/measurements")
def get_measurements(
    limit: int = Query(default=50, ge=1 ,le=200)
):
    with get_connection() as conn:
         rows = conn.execute(
             """
             SELECT id, sensor, value, created_at
             FROM measurements
             ORDER BY created_at DESC, id DESC
             LIMIT %s
             """,
             (limit,),
        ).fetchall()
    return rows
