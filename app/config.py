from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from app.api.utils import cleanup
from contextlib import asynccontextmanager

import asyncio
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск фоновой задачи при старте приложения
    cleanup_task = asyncio.create_task(cleanup())
    try:
        yield
    finally:
        # Остановка фоновой задачи при завершении приложения
        cleanup_task.cancel()
        await cleanup_task

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "app", "templates"))
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="app/static"), name="static")

if not os.path.exists('images'):
    os.makedirs('images')
app.mount("/images", StaticFiles(directory="images"), name="images")

clients = []

