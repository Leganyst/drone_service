from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

import os

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "app", "templates"))


