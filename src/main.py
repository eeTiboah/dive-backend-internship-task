
from fastapi import FastAPI
import logging

app = FastAPI()


logging.basicConfig(level=logging.INFO)

@app.get("/")
def index():
    return {"message": "Welcome to Calorie Intake Tracker API"}