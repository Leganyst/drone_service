import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2
import serial
import requests
import os
import json
from datetime import datetime

# Настройки GPIO
FIRE_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(FIRE_PIN, GPIO.IN)

# Настройки камеры
picam2 = Picamera2()
camera_config = picam2.create_still_configuration()
picam2.configure(camera_config)
picam2.start()

# Настройки GSM модуля
SERIAL_PORT = '/dev/serial0'  # или '/dev/ttyS0'
BAUD_RATE = 9600

# Попытка изменения прав доступа к порту
os.system(f'sudo chmod 666 {SERIAL_PORT}')

try:
    gsm = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

def send_at_command(command, timeout=1):
    try:
        gsm.write((command + '\r\n').encode())
        time.sleep(timeout)
        response = gsm.read_all().decode(errors='ignore')  # Игнорируем ошибки декодирования
        return response
    except Exception as e:
        print(f"Error during send_at_command: {e}")
        return ""

# Функция отправки данных на сервер
def send_data(timestamp):
    url = "http://hack.leganyst.ru/api/data"  # Замените на ваш URL сервера
    data = {
        "time": timestamp,
        "latitude": 65.4323,
        "longitude": 12.3122
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.status_code

# Функция отправки фото на сервер в бинарном формате
def send_photo(photo_path):
    url = "http://hack.leganyst.ru/api/data/photo"  # Замените на ваш URL сервера
    with open(photo_path, 'rb') as file:
        files = {"photo": file}
        response = requests.post(url, files=files)
    print(response)
    return response.status_code

# Настройка GPRS
send_at_command('AT')
send_at_command('AT+CPIN?')
send_at_command('AT+CREG?')
send_at_command('AT+CGATT=1')
send_at_command('AT+CSTT="internet.beeline.ru","beeline","beeline"')  # Установите ваш APN, имя пользователя и пароль
send_at_command('AT+CIICR')
send_at_command('AT+CIFSR')

try:
    while True:
        if GPIO.input(FIRE_PIN) == 0:
            print("Fire detected!")
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            photo_path = f"/home/admin/fire_{timestamp}.jpg"
            picam2.capture_file(photo_path)
            print(f"Photo taken: {photo_path}")

            data_response_code = send_data(timestamp)
            if data_response_code == 200:
                print("Data successfully uploaded to the server")
            else:
                print("Failed to upload data to the server")

            photo_response_code = send_photo(photo_path)
            if photo_response_code == 200:
                print("Photo successfully uploaded to the server")
            else:
                print("Failed to upload photo to the server")
            
            time.sleep(10)  # Задержка для предотвращения частого срабатывания

except KeyboardInterrupt:
    print("Program stopped")
finally:
    GPIO.cleanup()
    gsm.close()
    picam2.stop()
