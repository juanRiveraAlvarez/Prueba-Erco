import psycopg2
import textwrap
from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd

# Operators; we need this to operate!
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

# The DAG object; we'll need this to instantiate a DAG
from airflow.sdk import DAG
with DAG(
    "d1",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'on_skipped_callback': another_function, #or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="A simple tutorial DAG",
    schedule=timedelta(minutes=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

    N_SERVICES = 5
    N_DEVICES_PER_SERVICE = 20
    TOTAL_DEVICES = N_SERVICES * N_DEVICES_PER_SERVICE
    INTERVAL_MINUTES = 15
    HOURS = 24
    DAYS = 7
    DATA_POINTS = int(DAYS * HOURS * 60 / INTERVAL_MINUTES)
    START_DATE = datetime(2025, 7, 1, 0, 0)

    services_data = []
    devices_data = []
    records_data = []

    def solar_profile(hour):
        if 6 <= hour <= 18:
            x = (hour - 6) / 12 * np.pi
            return np.sin(x)
        else:
            return 0.0

    def consultar_ultima_fecha(**kwargs):
        try:
            conn = psycopg2.connect(
                host="postgres-datos",
                database="db",
                user="root",
                password="root",
                port=5432
            )
            cur = conn.cursor()
            cur.execute(
                "SELECT timestamp FROM record ORDER BY timestamp desc limit 1")
            (ultimo,) = cur.fetchone()
            cur.close()
            conn.close()
            if ultimo.hour == 18 and ultimo.minute == 45:
                nuevo = ultimo + timedelta(hours=11, minutes=15)
                print(nuevo)
                return nuevo
            elif ultimo.hour >= 6 and ultimo.hour < 19:
                print(ultimo)
                return ultimo
        except:
            print("ERROR IMPORTANDO LA ULTIMA FECHA")

    def generar_registros_dispositivos(**kwargs):
        ti = kwargs['ti']
        fecha = ti.xcom_pull(task_ids='consultar_ultima_fecha')
        print("La fecha que recibí es:", fecha)
        for device_id in range(1, TOTAL_DEVICES + 1):
            accumulated_energy = 0
            frozen = False
            t = fecha + timedelta(minutes=INTERVAL_MINUTES)
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

                accumulated_energy = max(
                    accumulated_energy + delta, accumulated_energy)
                records_data.append(
                    [device_id, t.isoformat(), round(accumulated_energy, 2)])

                conn = psycopg2.connect(
                    host="postgres-datos",
                    database="db",
                    user="root",
                    password="root",
                    port=5432
                )
                cur = conn.cursor()
                cur.execute("INSERT INTO record (device_id, timestamp, value) VALUES (%s, %s, %s)", (
                    device_id, t.isoformat(), round(accumulated_energy, 2)))
                conn.commit()
            cur.close()
            conn.close()
            print(records_data)

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t0 = PythonOperator(
        task_id="consultar_ultima_fecha",
        python_callable=consultar_ultima_fecha,
        dag=dag
    )

    t1 = PythonOperator(
        task_id="generar_registros_dispositivos",
        python_callable=generar_registros_dispositivos,
        dag=dag
    )
t0 >> t1
