from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from db.database import engine
from db.models import DataDroneORM

from app.config import clients

import os

data = APIRouter()

class DataDrone(BaseModel): 
    """
    Представляет собой модель принимаемых данных, в данном случае от дрона.
    Подразумевается, что дрон будет отправлять координаты (Ширина и долгота)
    и время отправки данных. Изображение должно по логике отправляться на соответствующий сервер с хранением
    различных данных, но в данной интерпретации мы будем его сохранять на той же машине.
    """
    time: str = Field(..., description='Время, представленное в виде строки вида дд.гг.чч чч:мм:сс', example="16.05.2024 18:43:34")
    latitude: float = Field(..., description='Широта', example=55.7522)
    longitude: float = Field(..., description='Долгота', example=37.6156)
    photo_path: Optional[str] = Field(None, description='Путь к сохраненной фотографии с дрона')


# @data.post("/api/data", tags= ["Информация от дрона"], response_model=DataDrone, response_description="Данные от дрона")
# def post_data(data: DataDrone, response: Response):
#     """
#     Принимает данные от дрона по модели DataDrone и сохраняет их в БД (Постгрес)
#     """
#     with Session(engine) as session:
#         data_orm = DataDroneORM(time=datetime.strptime(data.time, "%d.%m.%Y %H:%M:%S"), latitude=data.latitude, longitude=data.longitude)
#         # Добавляем в сессию
#         session.add(data_orm)
#         # Сохраняем
#         session.commit()

#     return data


@data.post(
    "/api/data",
    tags=["Информация от дрона"],
    response_model=DataDrone,
    summary="Отправить данные от дрона",
    description="Этот API принимает данные от дрона в виде объекта DataDrone, который содержит время, широту и долготу. Данные сохраняются в базе данных и отправляются всем подключенным клиентам через веб-сокеты.",
    response_description="Объект DataDrone, который был сохранен в базе данных и отправлен через веб-сокеты",
    operation_id="post_drone_data",
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Неверный запрос"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def post_data(data: DataDrone):
    data_orm = DataDroneORM(
        time=data.time,
        latitude=data.latitude,
        longitude=data.longitude
    )
    with Session(engine) as session:
        session.add(data_orm)
        session.commit()
        session.refresh(data_orm)
        data_dict = {
            "time": data_orm.time.strftime("%d.%m.%Y %H:%M:%S"),
            "latitude": data_orm.latitude,
            "longitude": data_orm.longitude
        }
    return data


@data.post(
    "/api/data/photo",
    tags=["Информация от дрона"],
    summary="Отправить фото от дрона",
    description="Этот API принимает фото от дрона и сохраняет его на сервере. Путь к фотографии затем сохраняется в базе данных.",
    operation_id="post_drone_photo",
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Неверный запрос"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def post_photo(photo: UploadFile = File(...)):
    with Session(engine) as session:
        data_orm = session.query(DataDroneORM).order_by(desc(DataDroneORM.time)).first()
        if not data_orm:
            raise HTTPException(status_code=400, detail="No data available to attach the photo")
        contents = await photo.read()
        file_name = f"{data_orm.id}.jpg"
        file_path = os.path.join("images", file_name)
        with open(file_path, "wb") as f:
            f.write(contents)
        data_orm.image_path = file_path
        session.commit()

        # Отправляем обновления через WebSocket после сохранения фотографии
        data_dict = {
            "time": data_orm.time.strftime("%d.%m.%Y %H:%M:%S"),
            "latitude": data_orm.latitude,
            "longitude": data_orm.longitude,
            "photo_url": f"/images/{file_name}"
        }
        for client in clients:
            await client.send_json(data_dict)

    return {"photo_url": f"/images/{file_name}"}


@data.get("/api/data", response_model=List[DataDrone], tags=["Информация от дрона"], summary="Получить данные от дрона")
async def get_data():
    """
    Получает данные о дронах, отсортированные по времени в порядке убывания.

    :return: Список объектов DataDrone, содержащих информацию о сообщениях дрона(ов).
    """
    with Session(engine) as session:
        data = session.query(DataDroneORM).order_by(desc(DataDroneORM.time)).all()
        return [
            DataDrone(
                time=d.time.strftime("%d.%m.%Y %H:%M:%S"),
                latitude=d.latitude,
                longitude=d.longitude,
                photo_path=d.image_path
            )
            for d in data
        ]