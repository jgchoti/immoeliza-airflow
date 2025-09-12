from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from pathlib import Path
import traceback
import sys
import os
sys.path.insert(0, "/opt/airflow/scripts")
sys.path.insert(0, "/opt/airflow/plugins")
from utils.output import Output  


try:
    from utils.property_scraper import PropertyScraper
    SCRAPER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: PropertyScraper not available: {e}")
    SCRAPER_AVAILABLE = False

default_args = {
    'owner': 'immo-eliza-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'immo_eliza_pipeline',
    default_args=default_args,
    description='Immo-Eliza pipeline storing data in PostgreSQL with deduplication',
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    tags=['real-estate', 'scraping', 'analysis'],
)

def check_dependencies(**context):
    missing_deps = []
    if not SCRAPER_AVAILABLE:
        missing_deps.append("utils.property_scraper.PropertyScraper")
    scripts_to_check = [
        "/opt/airflow/scripts/train_model.py",
        "/opt/airflow/scripts/generate_dashboard.py"
    ]
    for script in scripts_to_check:
        if not Path(script).exists():
            missing_deps.append(script)
    if missing_deps:
        error_msg = f"Missing dependencies: {missing_deps}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    print("✅ All dependencies available")
    return "All dependencies available"

def scrape_apartments_task(**context):
    if not SCRAPER_AVAILABLE:
        raise Exception("PropertyScraper not available")
    
    scraper = PropertyScraper(category_type="APARTMENT")
    
    try:
        summary = scraper.scrape_all_price_ranges()
        context['task_instance'].xcom_push(key='apartments_count', value=summary['total_properties'])  
        context['task_instance'].xcom_push(key='apartments_price_ranges_scraped', value=summary['price_ranges_scraped'])
        context['task_instance'].xcom_push(key='duration', value=summary['duration'])
        
        return summary['total_properties']
    finally:
        scraper.cleanup()

def scrape_houses_task(**context):
    if not SCRAPER_AVAILABLE:
        raise Exception("PropertyScraper not available")
    
    scraper = PropertyScraper(category_type="HOUSE")
    
    try:
        summary = scraper.scrape_all_price_ranges()
        context['task_instance'].xcom_push(key='houses_count', value=summary['total_properties'])
        context['task_instance'].xcom_push(key='houses_price_ranges_scraped', value=summary['price_ranges_scraped'])
        context['task_instance'].xcom_push(key='duration', value=summary['duration'])
        
        return summary['total_properties']
    finally:
        scraper.cleanup()

def deduplicate_task(**context):
    from utils.output import Output
    output = Output(postgres_conn_id='postgres_default')
    output.deduplicate(unique_col="zimmo_code")
    return "Deduplication complete"

def final_summary_task(**context):
    from utils.output import Output
    output = Output(postgres_conn_id='postgres_default')
    
    try:
        df = output.read_db() 
        total_properties = len(df)
        print(f"📊 Total properties in DB after deduplication: {total_properties}")
        return f"Pipeline completed successfully with {total_properties} properties processed!"
    except Exception as e:
        print(f"Error in final_summary_task: {e}")
        return f"Pipeline completed with errors: {e}"


def train_model_task(**context):
    from train_model import main as train_main
    return train_main()


def generate_dashboard_task(**context):
    from generate_dashboard import main as dashboard_main
    return dashboard_main()


train_model = PythonOperator(
    task_id="train_regression_model",
    python_callable=train_model_task,
    dag=dag,
)

generate_dashboard = PythonOperator(
    task_id="generate_dashboard_data",
    python_callable=generate_dashboard_task,
    dag=dag,
)


start_task = EmptyOperator(task_id='start_pipeline', dag=dag)


check_deps = PythonOperator(
    task_id='check_dependencies',
    python_callable=check_dependencies,
    dag=dag,
    retries=2, 
    retry_delay=timedelta(minutes=1)
)

scrape_apartments = PythonOperator(
    task_id='scrape_apartments',
    python_callable=scrape_apartments_task,
    dag=dag,
    

)

scrape_houses = PythonOperator(
    task_id='scrape_houses',
    python_callable=scrape_houses_task,
    dag=dag,

 
)

deduplicate_data = PythonOperator(
    task_id='deduplicate_data',
    python_callable=deduplicate_task,
    dag=dag
)

final_summary = PythonOperator(
    task_id='final_summary', 
    python_callable=final_summary_task, 
    dag=dag
)

end_task = EmptyOperator(task_id='end_pipeline', dag=dag)


start_task >> check_deps
check_deps >> scrape_apartments >> scrape_houses
scrape_houses >> deduplicate_data
deduplicate_data >> [train_model, generate_dashboard]
[train_model, generate_dashboard] >> final_summary
final_summary >> end_task
