from airflow.utils.edgemodifier import Label
from datetime import datetime, timedelta
from textwrap import dedent
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.models import Variable
import sqlite3
import pandas as pd

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


## Do not change the code below this line ---------------------!!#
def export_final_answer():
    import base64

    # Import count
    with open('count.txt') as f:
        count = f.readlines()[0]

    my_email = Variable.get("my_email")
    message = my_email+count
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')

    with open("final_output.txt","w") as f:
        f.write(base64_message)
    return None
## Do not change the code above this line-----------------------##

def extract_order_data(**context):
    conn = sqlite3.connect('./data/Northwind_small.sqlite')
    order_df = pd.read_sql_query('SELECT * from "Order";', conn)
    order_df.to_csv(f"data/output_orders{context['ds_nodash']}.csv")
    conn.close()

def calculate_rio_quantity(**context):
    conn = sqlite3.connect('./data/Northwind_small.sqlite')
    orderDetail_df = pd.read_sql_query('SELECT * from "OrderDetail";', conn)
    order_df = pd.read_csv(f"data/output_orders{context['ds_nodash']}.csv")
    merge_df = pd.merge(orderDetail_df, order_df, how="inner", left_on="OrderId", right_on="Id")
    finds_Rio_df = merge_df.query('ShipCity == "Rio de Janeiro"')
    count = str(finds_Rio_df['Quantity'].count())
    with open("count.txt", 'w') as f:
        f.write(count)
    conn.close()
    

with DAG(
    'DesafioAirflow',
    default_args=default_args,
    description='Desafio de Airflow da Indicium',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:
    dag.doc_md = """
        Esse é o desafio de Airflow da Indicium.
    """
   
    export_final_output = PythonOperator(
        task_id='export_final_output',
        python_callable=export_final_answer,
        provide_context=True
    )

    extract_order_data_task = PythonOperator (
        task_id = 'extract_order_data_task',
        python_callable=extract_order_data,
        provide_context=True
    )

    calculate_rio_quantity_task = PythonOperator (
        task_id = 'calculate_rio_quantity_task',
        python_callable=calculate_rio_quantity,
        provide_context=True
    )


extract_order_data_task >> calculate_rio_quantity_task >> export_final_output