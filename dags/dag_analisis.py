import psycopg2
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Operators; we need this to operate!
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

# The DAG object; we'll need this to instantiate a DAG
from airflow.sdk import DAG
with DAG(
    "a2",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
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

    def deteccion_valores_congelados(**kwargs):
        conn = psycopg2.connect(
            host="postgres-datos",
            database="db",
            user="root",
            password="root",
            port=5432
        )
        cur = conn.cursor()

        query = """
            SELECT *
            FROM (
            SELECT
                id,
                device_id,
                timestamp,
                value,
                ROW_NUMBER() OVER (PARTITION BY device_id ORDER BY timestamp DESC) AS rn
            FROM record
            WHERE EXTRACT(HOUR FROM timestamp) BETWEEN 7 AND 17
            ) sub
            WHERE rn <= 3
            ORDER BY device_id, timestamp;
        """

        df = pd.read_sql(query, conn)
        congelados = []

        for id ,group in df.groupby("id"):
            valores = group["value"].tolist()
            if len(valores) == 3 and all(v == valores[0] for v in valores):
                congelados.append(id)
                
           
                cur.execute("UPDATE record SET status = 'cuarentena' WHERE id = %s", [id])
   
                conn.commit()
        cur.close()
        conn.close()
        if(len(congelados) == 0):
            print("todo bien")
        else:
            print("Hay congelados ", congelados)

    def detectar_desviacion(**kwargs):
        
            conn = psycopg2.connect(
                host='postgres-datos',
                database='db',
                user='root',
                password='root',
                port=5432
            )

            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM device",)
            (dispositivos,) = cur.fetchone()
            franjas = [8,10,12,14]
            for f in franjas:
                    for i in range(1,dispositivos+1):
                        print(f"franja {f} - {f+2}")
                        cur.execute(f"""
                                    SELECT * 
                                    FROM record 
                                    where 
                                        EXTRACT(HOUR FROM timestamp)<={f+2} and
                                        EXTRACT(HOUR FROM timestamp) >={f} and 
                                        device_id = {i} and
                                        status = 'valido'
                                    ORDER BY timestamp desc limit 1;
                                    """)
                        ultimo = cur.fetchone()
                        print(f"ultimo {ultimo}")
                    
                        cur.execute(f"""
                                    SELECT
                                        device_id,
                                        timestamp,
                                        value
                                        FROM record
                                    WHERE 
                                        EXTRACT(HOUR FROM timestamp) <= {f+2} and
                                        EXTRACT(HOUR FROM timestamp) >= {f} and 
                                        device_id = {i} and
                                        status = 'valido' and
                                        EXTRACT(DAY FROM timestamp)<15
                                        
                                    """)
                        historico = list(map(lambda x : x[2] ,cur.fetchall()))[:-1]
                        for j in range(1,len(historico)):
                            if historico[j] < historico[j-1]:
                                print("Dato atipico")
                                cur.execute("UPDATE record SET status = 'cuarentena' WHERE id = %s", [ultimo[0]])
                                conn.commit()
                                
                        print(historico)
                        media = np.mean(historico)
                        desviacion_estandar = np.std(historico)
                        lim_inf = media - 2 * desviacion_estandar
                        lim_sup = media + 2 * desviacion_estandar
                        print(f"media {media} - desviacion {desviacion_estandar}")
                        print(f"lim_inf {lim_inf}")
                        print(f"lim_sup {lim_sup}")
                        if ultimo[3] > lim_sup and ultimo[3] < 0:
                            cur.execute("UPDATE record SET status = 'cuarentena' WHERE id = %s", [ultimo[0]])
                            conn.commit()
                            print("Dato atipico")
                            

                        print("CORRECTO")
            cur.close()
            conn.close()




    t0 = PythonOperator(
        task_id="deteccion_valores_congelados",
        python_callable=deteccion_valores_congelados,
        dag=dag
    )

    t1 = PythonOperator(
        task_id="detectar_desviacion",
        python_callable=detectar_desviacion,
        dag=dag
    )
t0 >> t1
