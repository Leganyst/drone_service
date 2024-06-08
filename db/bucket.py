import influxdb_client, os
from influxdb_client.client.write_api import SYNCHRONOUS

# Токен для Indflux, выдается после создания аккаунта
token = os.environ.get("INFLUXDB_TOKEN")
# Название организации, указывается при реге
org = "pidregulator"
# URL на котором эта дура развернута
url = "http://localhost:8086"
# Соответственно сам экземпляр для работы с данной БД
# client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, password="adminadmin", username="admin", debug=True)

# Хранилище, оно же ведро
bucket="drone"
# Непосредственно объект API для записи
write_api = client.write_api(write_options=SYNCHRONOUS)
# API для чтения из базы
query_api = client.query_api()
# API для удаления данных
delete_api = client.delete_api()
