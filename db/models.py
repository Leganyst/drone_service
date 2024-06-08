from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class DataDroneORM(Base):
    __tablename__ = "drone_data"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    time: Mapped[datetime] = mapped_column()
    latitude: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column(nullable=True)
    image_path: Mapped[str] = mapped_column(nullable=True)