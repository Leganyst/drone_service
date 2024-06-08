from app.config import app, templates
from app.api.get_data import data
from db.models import Base
from db.database import engine
from app.index import *

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app.include_router(data)
