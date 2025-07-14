# Proyecto ERCO – Análisis de Datos de Energía con Airflow

Este proyecto realiza la simulación y análisis de datos de generación de energía para distintos dispositivos, utilizando Apache Airflow, PostgreSQL y Redis.

## 🔧 Requisitos

- Docker
- Docker Compose

## 🚀 Ejecución del proyecto

Sigue estos pasos para levantar el entorno completo de desarrollo con Apache Airflow:

### 1. Clonar el repo
### 1. Ejecutar los siguientes comandos a la altura del docker-compose.yml

```bash
docker compose run airflow-cli airflow config list
docker compose up airflow-init
docker compose up
