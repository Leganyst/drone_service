from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

import os

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "app", "templates"))
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

if not os.path.exists('images'):
    os.makedirs('images')
app.mount("/images", StaticFiles(directory="images"), name="images")

clients = []

class Config:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "postgres")
    DB_NAME = os.getenv("DB_NAME", "project")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")