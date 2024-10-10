from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.utils.email import send_email
import datetime

# Email notification function
def notify_email(context):
    subject = f"Airflow Task Failure: {context['task_instance_key_str']}"
    body = f"""
    DAG: {context['task_instance'].dag_id}<br>
    Task: {context['task_instance'].task_id}<br>
    Execution Time: {context['execution_date']}<br>
    Log URL: {context['task_instance'].log_url}
    """
    send_email(to="your_email@example.com", subject=subject, html_content=body)

# Define default_args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['your_email@example.com'],  # Your email address here
    'on_failure_callback': notify_email,
    'start_date': days_ago(1),
}

# Define the DAG
dag = DAG(
    'bash_operator_dag',
    default_args=default_args,
    schedule_interval='0 19 * * *',
    catchup=False,
)

# Task 1 - BashOperator to run python script 1
task_1 = BashOperator(
    task_id='finshot_Scraper',
    bash_command='python3 ../scripts/finshot_scaper.py',
    dag=dag
)


task_2 = BashOperator(
    task_id='movie_100k_ml',
    bash_command='python3 ../scripts/pipeline2.py',
    dag=dag
)

task_1 >> task_2
