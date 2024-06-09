from sqlalchemy import create_engine

import os
class Config:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "postgres")
    DB_NAME = os.getenv("DB_NAME", "project")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")

try:
    engine = create_engine(
        f"postgresql+psycopg2://{Config.DB_USER}:{Config.DB_PASS}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}",
        echo=True
    )
except Exception as e:
    print(e, " )))))))")
    