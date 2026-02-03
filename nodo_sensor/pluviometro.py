# /home/luis/proyecto_sensores/pluviometro.py

import os
import time
from datetime import date

# Fuerza backend pigpio (más estable que RPi.GPIO para edge detection)
# OJO: esto debe ir ANTES de importar gpiozero
os.environ.setdefault("GPIOZERO_PIN_FACTORY", "pigpio")

from gpiozero import Button

# ====== CONFIG ======
PIN_PLUVIO_BCM = 6          # pin físico 31 => BCM 6
MM_POR_TIP = 0.3            # WH-SR-RG típico (luego calibramos)
BOUNCE_S = 0.03             # anti-rebote (30 ms)

# ====== ESTADO GLOBAL ======
_btn = None
_tips_intervalo = 0
_tips_dia = 0
_last_tip_ts = 0.0
_dia_actual = date.today()

def _reset_diario_si_cambio():
    """Si cambió el día (medianoche), reinicia contador diario."""
    global _dia_actual, _tips_dia
    hoy = date.today()
    if hoy != _dia_actual:
        _dia_actual = hoy
        _tips_dia = 0

def _on_tip():
    global _tips_intervalo, _tips_dia, _last_tip_ts
    now = time.time()

    # Filtro extra por tiempo (además del bounce_time) por si acaso
    if (now - _last_tip_ts) < 0.02:
        return

    _last_tip_ts = now

    _reset_diario_si_cambio()
    _tips_intervalo += 1
    _tips_dia += 1

def iniciar_pluvio():
    """Inicializa el contador una sola vez."""
    global _btn, _dia_actual
    _reset_diario_si_cambio()
    if _btn is None:
        _btn = Button(PIN_PLUVIO_BCM, pull_up=True, bounce_time=BOUNCE_S)
        _btn.when_pressed = _on_tip

def leer_pluvio_y_reset():
    """
    Devuelve lluvia acumulada desde la última lectura (intervalo) y reinicia SOLO el intervalo.
    También devuelve acumulado diario.
    """
    global _tips_intervalo
    iniciar_pluvio()
    _reset_diario_si_cambio()

    tips_int = _tips_intervalo
    _tips_intervalo = 0

    return {
        "lluvia_tips_intervalo": int(tips_int),
        "lluvia_mm_intervalo": round(tips_int * MM_POR_TIP, 3),
        "lluvia_tips_dia": int(_tips_dia),
        "lluvia_mm_dia": round(_tips_dia * MM_POR_TIP, 3),
    }

# Test manual: muestra tips/mm acumulados (sin reset) en vivo
if __name__ == "__main__":
    iniciar_pluvio()
    print("✅ Pluviómetro listo. Mueve el balancín... (CTRL+C para salir)")
    try:
        while True:
            time.sleep(1)
            _reset_diario_si_cambio()
            print(
                "tips intervalo:", _tips_intervalo,
                "mm intervalo:", round(_tips_intervalo * MM_POR_TIP, 3),
                "| tips día:", _tips_dia,
                "mm día:", round(_tips_dia * MM_POR_TIP, 3),
            )
    except KeyboardInterrupt:
        print("\n🛑 Fin.")
