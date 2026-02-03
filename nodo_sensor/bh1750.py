
import time
import board
import busio
import adafruit_bh1750

# Mantén instancias globales, pero NO inicialices al importar.
_i2c = None
_bh = None
_last_fail_ts = 0


def _get_bh1750():
    """
    Inicializa BH1750 solo cuando se necesita.
    Si el bus está 'ocupado' o falla, lo reintenta luego.
    """
    global _i2c, _bh, _last_fail_ts

    # Si falló hace poco, espera un poco para no golpear el bus I2C
    if _bh is None and (time.time() - _last_fail_ts) < 2:
        raise OSError("BH1750: reintento muy pronto (cooldown)")

    if _bh is None:
        try:
            if _i2c is None:
                _i2c = busio.I2C(board.SCL, board.SDA)
            _bh = adafruit_bh1750.BH1750(_i2c)
        except Exception as e:
            _bh = None
            _last_fail_ts = time.time()
            raise e

    return _bh


def leer_bh1750():
    """
    Lee lux. Si falla, devuelve None en lux (no revienta el sistema).
    """
    try:
        bh = _get_bh1750()
        return {"lux": round(bh.lux, 2)}
    except Exception as e:
        # Importante: no tirar excepción
        return {"lux": None}


# Test simple si se ejecuta directamente
if __name__ == "__main__":
    print(leer_bh1750())
