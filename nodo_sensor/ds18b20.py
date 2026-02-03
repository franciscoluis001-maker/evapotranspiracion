import glob

def leer_ds18b20():
    base_dir = '/sys/bus/w1/devices/'
    devices = glob.glob(base_dir + '28*')
    if not devices:
        return {"temperatura_suelo": None}

    device_folder = devices[0]
    device_file = device_folder + '/w1_slave'
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
        if lines[0].strip()[-3:] != 'YES':
            return {"temperatura_suelo": None}
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_c = float(lines[1][equals_pos+2:]) / 1000.0
            return {"temperatura_suelo": round(temp_c, 2)}
    except Exception:
        return {"temperatura_suelo": None}
