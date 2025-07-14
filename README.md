# Proyecto ERCO – Análisis de Datos de Energía con Airflow

Este proyecto realiza la simulación y análisis de datos de generación de energía para distintos dispositivos, utilizando Apache Airflow y PostgreSQL.

## 🔧 Requisitos

- Docker
- Docker Compose

## 🚀 Ejecución del proyecto

Sigue estos pasos para levantar el entorno completo de desarrollo con Apache Airflow:

### 1. Clonar el repo
### 2. Ejecutar los siguientes comandos a la altura del docker-compose.yml

```bash
docker compose run airflow-cli airflow config list
docker compose up airflow-init
docker compose up
```

## Crear la base de datos
Usar el script Script-2.sql para crear la estructura de tabas necesaria
Las credenciales para la base de datos son: host: "localhost", database:"db", user:"root", password:"root", port:5432

## Como usarlo
Una vez levantado el servido (Se puede tardar varios minutos) acceder a localhost:8080 y seguir los siguientes pasos

### 1. Iniciar sesion
El usuario y contrasena por defecto son {Usuario: airflow, Contrasena: airflow} tal cual esta en el docker-compose.yml

### 2. Buscar dag
Te dirijes al apartado de Dags

img

Y buscas el dag por el nombre que tiene en el proyecto en este caso los dags a buscar son: cargar_d, d1 y a2

### 3. Correr cargar_d
Se debe correr primero este dag pues este genera todos los datos necesarios para poder luego analisar los procesos

### 4, Correr a2
Esta dag se encarga de realizar analisis con los datos ingresados, es normal que no arroje alertas la primera vez que se corre para ello el la base de datos vamos a correr:

```sql
INSERT INTO record (device_id, timestamp, value)
VALUES 
  (1, '2025-07-08 08:15:00', 300),
  (1, '2025-07-08 08:30:00', 410),
  (1, '2025-07-08 08:45:00', 520);

INSERT INTO record (device_id, timestamp, value)
VALUES 
  (1, '2025-07-08 10:15:00', 0),
  (1, '2025-07-08 10:30:00', 0),
  (1, '2025-07-08 10:45:00', 0);
```
Son casos particules que ponene a prueba el sistema, en el primer caso son valores altos para el contexto de los datos recibidos la primera semana y al salirse del intervalo estimado estos entran en cuarentena, el segundo caso pone a prueba el sistema si los valores se quedan estaticos, y entran tambien en cuarentena.

Si se corre a2 nuevamente y se consulta la consola y la base de datos se podra ver como estos valores al no ser validos segun el analisis entran a cuarentena.

