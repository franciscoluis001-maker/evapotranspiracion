import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime, date
import math

# =============================
# CONFIGURACIÓN GENERAL
# =============================

DB_NAME = "/home/luis/coordinador/sensores_data.db"
TOPIC = "estacion/sensores/lecturas"

LATITUD = 0.322580  # Ibarra, Ecuador (grados)
ALTITUD = 2225     # metros sobre el nivel del mar (aprox. Ibarra)

# =============================
# FUNCIONES FAO-56
# =============================

def dia_juliano():
    return date.today().timetuple().tm_yday

def radiacion_extraterrestre_MJ(lat, J):
    """Ra en MJ/m²/día (FAO-56)"""
    Gsc = 0.0820  # MJ m-2 min-1
    phi = math.radians(lat)
    dr = 1 + 0.033 * math.cos(2 * math.pi * J / 365)
    delta = 0.409 * math.sin((2 * math.pi * J / 365) - 1.39)
    ws = math.acos(-math.tan(phi) * math.tan(delta))

    Ra = (24 * 60 / math.pi) * Gsc * dr * (
        ws * math.sin(phi) * math.sin(delta) +
        math.cos(phi) * math.cos(delta) * math.sin(ws)
    )
    return Ra

def presion_kpa(alt):
    return 101.3 * ((293 - 0.0065 * alt) / 293) ** 5.26

def calcular_et0_diaria(T, HR, u2):
    """
    FAO-56 Penman-Monteith diaria
    Rs estimada a partir de Ra
    """

    J = dia_juliano()
    Ra = radiacion_extraterrestre_MJ(LATITUD, J)

    # Estimación Rs FAO (cielo despejado aproximado)
    Rs = 0.75 * Ra

    P = presion_kpa(ALTITUD)
    gamma = 0.665e-3 * P

    es = 0.6108 * math.exp((17.27 * T) / (T + 237.3))
    ea = es * HR / 100
    delta = 4098 * es / ((T + 237.3) ** 2)

    et0 = (
        (0.408 * delta * Rs) +
        gamma * (900 / (T + 273)) * u2 * (es - ea)
    ) / (
        delta + gamma * (1 + 0.34 * u2)
    )

    return round(max(et0, 0), 3)

# =============================
# BASE DE DATOS
# =============================

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS lecturas (
    timestamp TEXT,
    temperatura REAL,
    humedad REAL,
    presion REAL,
    lux REAL,
    temperatura_suelo REAL,
    vel_viento REAL,
    lluvia REAL,
    et0 REAL
)
""")
conn.commit()

# =============================
# MQTT CALLBACK
# =============================

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        T = payload.get("temperatura")
        HR = payload.get("humedad")
        u2 = payload.get("vel_viento", 0.0)

        et0 = calcular_et0_diaria(T, HR, u2)

        datos = (
            now,
            T,
            HR,
            payload.get("presion"),
            payload.get("lux"),
            payload.get("temperatura_suelo"),
            u2,
            payload.get("lluvia_mm", 0),
            et0
        )

        cursor.execute("""
        INSERT INTO lecturas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, datos)
        conn.commit()

        print("\n🟢 Registro almacenado:")
        print(f"  Timestamp: {now}")
        print(f"  ET₀ diaria: {et0} mm/día")

    except Exception as e:
        print("⚠️ Error:", e)

# =============================
# MQTT SETUP
# =============================

MQTT_BROKER = "826882b2e6df43bfadc52a3df05b90c0.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "luismqtt"
MQTT_PASSWORD = "Aerosmith@18"

client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.tls_set()
client.on_message = on_message

print(f"📡 Conectando a HiveMQ ({TOPIC})")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(TOPIC)

client.loop_forever()
