import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA)
_bme = None

def _init_bme():
    global _bme
    try:
        _bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    except Exception:
        _bme = None

def leer_bme280():
    global _bme
    if _bme is None:
        _init_bme()
    if _bme is None:
        return {"temperatura": None, "humedad": None, "presion": None}

    try:
        return {
            "temperatura": round(_bme.temperature, 2),
            "humedad": round(_bme.humidity, 2),
            "presion": round(_bme.pressure, 2),
        }
    except Exception:
        return {"temperatura": None, "humedad": None, "presion": None}