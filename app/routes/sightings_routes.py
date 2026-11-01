from fastapi import FastAPI
from ..config import EXTERNAL_API_URL;

app = FastAPI()

@app.get("/tick-sightings")
def read_root():
    return {"message": "Hello, no world"}