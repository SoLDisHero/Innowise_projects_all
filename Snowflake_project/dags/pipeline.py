from airflow.sdk import dag, task
from pendulum import datetime
from airflow.providers.snowflake.operators.snowflake import SQLExecuteQueryOperator

@dag(
    dag_id="pipeline",
    start_date=datetime(2026,6,1),
    description="Snowflake loading pipeline data",
    tags=["snowlake", "airline"],
    schedule=None,
    catchup=False
)
def pipeline():

    transforming_task = SQLExecuteQueryOperator(
        conn_id="snowflake_conn",
        task_id="transforming_task",
        sql="CALL transform_schema.transform_to_procedure();",
        autocommit=True
    )

    loading_task = SQLExecuteQueryOperator(
        conn_id="snowflake_conn",
        task_id="loading_task",
        sql="CALL load_schema.load_data_procedure();",
        autocommit=True
    )
    transforming_task >> loading_task

pipeline()
