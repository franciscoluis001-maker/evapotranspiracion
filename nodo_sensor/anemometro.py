import RPi.GPIO as GPIO
import time

WIND_PIN = 5          # GPIO del anemómetro
INTERVALO = 5         # segundos para conteo
PULSO_A_VELOCIDAD = 1.2  # factor (m/s por pulso/s)

# Configuración GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(WIND_PIN, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

def leer_anemometro():
    """Cuenta pulsos en un intervalo y retorna un dict con 'vel_viento' en m/s."""
    last_state = GPIO.input(WIND_PIN)
    pulse_count = 0
    start_time = time.time()

    while time.time() - start_time < INTERVALO:
        current_state = GPIO.input(WIND_PIN)
        # Flanco LOW->HIGH
        if last_state == GPIO.LOW and current_state == GPIO.HIGH:
            pulse_count += 1
        last_state = current_state
        time.sleep(0.005)  # pequeño delay para evitar saturar CPU

    pps = pulse_count / INTERVALO  # pulsos por segundo
    velocidad = pps * PULSO_A_VELOCIDAD
    return {"vel_viento": round(velocidad, 2)}

# Test simple si se ejecuta directamente
if __name__ == "__main__":
    print("Probando anemómetro...")
    try:
        while True:
            print(leer_anemometro())
    except KeyboardInterrupt:
        GPIO.cleanup()