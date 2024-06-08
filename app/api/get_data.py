from fastapi import APIRouter, Response
from influxdb_client import Point, WritePrecision
from pydantic import BaseModel, Field
from typing import List 

from db.bucket import write_api, query_api

from datetime import datetime, timezone
from influxdb_client import InfluxDBClient

data = APIRouter()

class DataDrone(BaseModel): 
    """
    Представляет собой модель принимаемых данных, в данном случае от дрона.
    Подразумевается, что дрон будет отправлять координаты (Ширина и долгота)
    и время отправки данных. Изображение должно по логике отправляться на соответствующий сервер с хранением
    различных данных, но в данной интерпретации мы будем его сохранять на той же машине.
    """
    time: str = Field(..., description='Время, представленное в виде строки вида дд-гг-чч чч:мм:сс', example="16.05.2024 18:43:34")
    latitude: float = Field(..., description='Широта', example=55.7522)
    longitude: float = Field(..., description='Долгота', example=37.6156)

@data.post("/api/data", tags= ["Информация от дрона"], response_model=DataDrone, response_description="Данные от дрона")
def post_data(data: DataDrone, response: Response):
    """
    Принимает данные от дрона по модели DataDrone и сохраняет их в influx
    """
    # Создание точки для записи в Influx 
    point = Point("drone_data")\
        .field("drone_time", data.time)\
        .field("latitude", data.latitude)\
        .field("longitude", data.longitude)\
        .time(datetime.now(timezone.utc), WritePrecision.NS)
    
    # Непосредственно запись
    write_api.write(bucket="drone", record=point)
    return data


@data.get(
    "/api/data", 
    tags=["Информация от дрона"], 
    response_model=List[DataDrone],
    summary="Получить данные от дрона",
    description="Этот API возвращает список данных, полученных от дрона. Каждый элемент списка представляет собой объект DataDrone, который содержит время, широту и долготу.",
    response_description="Список объектов DataDrone",
    operation_id="get_drone_data",
    responses={
        200: {"description": "Успешный ответ"},
        400: {"description": "Неверный запрос"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
def get_data():
    """
    Возвращает все данные, которые были отправлены дроном
    """
    # Формируем запрос, что к чему откуда
    query = 'from(bucket: "drone") |> range(start: -1d)'
    result = query_api.query(query=query)
    
    # Наш результат
    data = []
    # Просматриваем все полученные ответы
    for table in result:
        # Для каждой записи из всех
        for record in table.records:
            # Получаем время
            time = record.get_field("drone_time")
            # Получаем поля
            latitude = record.get_field("latitude")
            longitude = record.get_field("longitude")
            # Добавляем в список объект DataDrone с указанными параметрами
            data.append(DataDrone(time=time, latitude=latitude, longitude=longitude))
    
    return data
 