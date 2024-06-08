from app.config import app
from app.api.get_data import data

app.include_router(data)

