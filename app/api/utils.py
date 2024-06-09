
from sqlalchemy import delete
from sqlalchemy.orm import Session

from db.database import engine
from db.models import DataDroneORM

import asyncio

async def cleanup():
    while True:
        with Session(engine) as session:
            stmt = delete(DataDroneORM).where(DataDroneORM.image_path.is_(None))
            session.execute(stmt)
            session.commit()
        await asyncio.sleep(300)
        
