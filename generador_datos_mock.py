import csv
import random
import datetime
import numpy as np
import pandas as pd

# Configuración
N_SERVICES = 5
N_DEVICES_PER_SERVICE = 20
TOTAL_DEVICES = N_SERVICES * N_DEVICES_PER_SERVICE
INTERVAL_MINUTES = 15
HOURS = 24
DAYS = 7
DATA_POINTS = int(DAYS * HOURS * 60 / INTERVAL_MINUTES)
START_DATE = datetime.datetime(2025, 7, 1, 0, 0)

# Generación solar con forma de campana entre 6am y 6pm
def solar_profile(hour):
    if 6 <= hour <= 18:
        x = (hour - 6) / 12 * np.pi
        return np.sin(x)
    else:
        return 0.0

# Contenedores para los datos
services_data = []
devices_data = []
records_data = []

# Generar servicios y dispositivos
device_id_counter = 1
for service_id in range(1, N_SERVICES + 1):
    services_data.append([service_id, f"Proyecto_{service_id}"])
    for _ in range(N_DEVICES_PER_SERVICE):
        devices_data.append([device_id_counter, service_id])
        device_id_counter += 1

# Generar registros por dispositivo (solo entre 6am y 6pm)
for device_id in range(1, TOTAL_DEVICES + 1):
    accumulated_energy = 0
    frozen = False

    for i in range(DATA_POINTS):
        t = START_DATE + datetime.timedelta(minutes=INTERVAL_MINUTES * i)
        solar_hour = t.hour

        if 6 <= solar_hour <= 18:
            base_gen = solar_profile(solar_hour)
            delta = base_gen * random.uniform(0.5, 1.5)

            if random.random() < 0.01:
                delta = -random.uniform(0.1, 0.5)
            elif random.random() < 0.01:
                delta *= 8
            elif random.random() < 0.02 and not frozen:
                delta = 0
                frozen = True
            else:
                frozen = False

            accumulated_energy = max(accumulated_energy + delta, accumulated_energy)
            records_data.append([device_id, t.isoformat(), round(accumulated_energy, 2)])

# Crear DataFrames y exportar CSV
services_df = pd.DataFrame(services_data, columns=["id_service", "name"])
devices_df = pd.DataFrame(devices_data, columns=["id_device", "id_service"])
records_df = pd.DataFrame(records_data, columns=["id_device", "timestamp", "value"])

services_df.to_csv("services.csv", index=False)
devices_df.to_csv("devices.csv", index=False)
records_df.to_csv("records.csv", index=False)

print("Archivos generados: services.csv, devices.csv, records.csv")
