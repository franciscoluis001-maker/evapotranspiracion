# sensores/capacitivo.py
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# Inicialización SPI y MCP3008
spi = busio.SPI(board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
cs.direction = digitalio.Direction.OUTPUT
mcp = MCP.MCP3008(spi, cs)
canal = AnalogIn(mcp, MCP.P0)

# Calibración personalizada (ajusta si es necesario):
V_SECO = 1.90    # voltaje en seco
V_MOJADO = 0.864 # voltaje en agua

def leer_humedad_capacitivo():
    voltaje = canal.voltage
    humedad = (V_SECO - voltaje) / (V_SECO - V_MOJADO) * 100
    humedad = max(0.0, min(100.0, humedad))
    return {"humedad": round(humedad, 2), "voltaje": round(voltaje, 3)}

# Test simple si se ejecuta directamente
if __name__ == "__main__":
    import time
    print("Probando sensor capacitivo (Ctrl+C para salir)...")
    while True:
        datos = leer_humedad_capacitivo()
        print(datos)
        time.sleep(2)