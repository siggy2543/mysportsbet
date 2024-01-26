# app.py

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

import requests

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 2, 20),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'bet_data_pipeline',
    default_args=default_args,
    description='Pipeline for ingesting ESPN bet data',
    schedule_interval=timedelta(days=1),
)

def extract_bets():
    url = "http://localhost:5000/bets"
    response = requests.get(url)
    bets = response.json()
    # Logic to store bets data

extract_bets_task = PythonOperator(
    task_id='extract_bets_task',
    python_callable=extract_bets,
    dag=dag
)