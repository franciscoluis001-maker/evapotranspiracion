# et0.py

import math
from datetime import datetime

def calcular_et0(temp_c, hr, Rs_lux, u2, presion_kpa, latitud_deg=-1.0, altitud_m=250):
    """
    Calcula la evapotranspiración de referencia (ET0) en mm/día usando Penman-Monteith FAO-56.

    Parámetros:
    - temp_c: Temperatura del aire (°C)
    - hr: Humedad relativa (%)
    - Rs_lux: Radiación solar en lux (se convertirá a MJ/m2/día)
    - u2: Velocidad del viento (m/s)
    - presion_kpa: Presión atmosférica (kPa)
    - latitud_deg: Latitud del sitio (grados decimales, negativa si es sur)
    - altitud_m: Altitud sobre el nivel del mar (m)

    Retorna:
    - ET0 en mm/día
    """

    # 1. Constantes
    Gsc = 0.0820  # Constante solar (MJ/m2/min)
    sigma = 4.903e-9  # Constante de Stefan-Boltzmann (MJ/K4/m2/día)

    # 2. Calcular presión de saturación y pendiente de la curva
    es = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))  # kPa
    ea = es * (hr / 100.0)  # presión de vapor actual
    delta = 4098 * es / ((temp_c + 237.3) ** 2)  # pendiente curva de presión
    gamma = 0.665e-3 * presion_kpa  # constante psicrométrica

    # 3. Radiación solar en MJ/m²/día (de lux a MJ/m2/día)
    Rs = Rs_lux * 0.0079

    # 4. Fecha y día juliano
    hoy = datetime.utcnow().date()
    dia_juliano = hoy.timetuple().tm_yday

    # 5. Calcular radiación extraterrestre (Ra)
    lat_rad = math.radians(latitud_deg)
    dr = 1 + 0.033 * math.cos(2 * math.pi / 365 * dia_juliano)
    delta_sol = 0.409 * math.sin(2 * math.pi / 365 * dia_juliano - 1.39)
    ws = math.acos(-math.tan(lat_rad) * math.tan(delta_sol))
    Ra = (24 * 60 / math.pi) * Gsc * dr * (
        ws * math.sin(lat_rad) * math.sin(delta_sol) +
        math.cos(lat_rad) * math.cos(delta_sol) * math.sin(ws)
    )  # MJ/m²/día

    # 6. Calcular Rso y Rns
    Rso = (0.75 + 2e-5 * altitud_m) * Ra
    Rns = (1 - 0.23) * Rs  # net shortwave radiation

    # 7. Calcular Rnl (radiación neta de onda larga)
    temp_k = temp_c + 273.15
    Rnl = sigma * ((temp_k ** 4 + temp_k ** 4) / 2) * \
          (0.34 - 0.14 * math.sqrt(ea)) * (1.35 * Rs / Rso - 0.35)

    Rn = Rns - Rnl  # Radiación neta total

    # 8. Calcular ET0 (Penman-Monteith FAO-56)
    et0 = (0.408 * delta * Rn + gamma * (900 / (temp_c + 273)) * u2 * (es - ea)) / \
          (delta + gamma * (1 + 0.34 * u2))

    return round(et0, 3)
