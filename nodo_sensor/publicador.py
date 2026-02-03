import time
import json
import paho.mqtt.client as mqtt

# Funciones de sensores
from bme280 import leer_bme280
from bh1750 import leer_bh1750
from ds18b20 import leer_ds18b20
# from capacitivo import leer_humedad_capacitivo
from anemometro import leer_anemometro
from pluviometro import leer_pluvio_y_reset

# Configuración MQTT HiveMQ Cloud
MQTT_BROKER = "826882b2e6df43bfadc52a3df05b90c0.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "luismqtt"
MQTT_PASSWORD = "Aerosmith@18"
MQTT_TOPIC = "estacion/sensores/lecturas"

INTERVALO_ENVIO = 300  # segundos (30 min)

# Configurar cliente MQTT
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.tls_set()  # Usa TLS

client.connect(MQTT_BROKER, MQTT_PORT, 60)
print(f"🌐 Publicando a {MQTT_TOPIC} cada {INTERVALO_ENVIO}s")

try:
    while True:
        # Lectura de sensores
        bme = leer_bme280()
        luz = leer_bh1750()
        temp_suelo = leer_ds18b20()
        # hum_cap = leer_humedad_capacitivo()
        viento = leer_anemometro()

        lluvia = leer_pluvio_y_reset()  # devuelve dict con lluvia_tips y lluvia_mm (intervalo)

        # Compatibilidad: mantener campo "lluvia" como antes (tips)
        lluvia_compat = {"lluvia": lluvia.get("lluvia_tips", 0)}

        # Unir en un solo diccionario
        payload = {
            **bme,
            **luz,
            **temp_suelo,
            # **hum_cap,
            **viento,
            **lluvia,         # lluvia_tips, lluvia_mm
            **lluvia_compat,  # lluvia (tips) para tu BD actual
        }

        client.publish(MQTT_TOPIC, json.dumps(payload))
        print(f"✅ Publicado: {payload}")

        time.sleep(INTERVALO_ENVIO)

except KeyboardInterrupt:
    client.disconnect()
    print("\n🛑 Publicador detenido por el usuario.")