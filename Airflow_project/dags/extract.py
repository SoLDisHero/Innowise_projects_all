from airflow.sdk import dag, task, task_group, Asset
from pendulum import datetime
from airflow.providers.standard.sensors.filesystem import FileSensor

import pandas as pd
import os

file="/usr/local/airflow/include/dataset/tiktok_google_play_reviews.csv"
dir_processed="/usr/local/airflow/include/processed/"

@dag(
    start_date=datetime(2026,1,1),
    schedule=None,
    tags=["extract", "dataset"],
    description="Transforming data",
    catchup=False
)
def wait_for_dataset():
  
    wait_for_file = FileSensor(
        task_id="wait_for_file",
        filepath=file,
        fs_conn_id="fs_default",
        poke_interval=33,
        timeout=600,
        mode="reschedule"
    )

    # BRANCH CHECK IF FILE EMPTY

    @task.branch
    def check_branch_file():
        if os.path.getsize(file) > 0:
            return "read_file"
        else:
            return "empty_file"
   
    # EMPTY

    @task.bash
    def empty_file():
        return f"echo 'The file has no data. Try out another one.'"
        
    # NOT EMPTY

    @task
    def read_file():
        data = pd.read_csv(file, low_memory=False)
        # because of the OOM, created the reference to the file
        processed_file = f"{dir_processed}read_data.csv"
        data.to_csv(processed_file, index=False)
        return processed_file
    
    # TASK GROUP DATA EDA

    @task_group(group_id="data_explore")
    def data_explore(data):
    # REPLACE NULL WITH "-"
        @task
        def null_data(data):
            data = pd.read_csv(data)
            # replacing all string columns with "-"
            string_col = data.select_dtypes(include=["object"]).columns
            data[string_col] = data[string_col].fillna("-")
            # because of the OOM, created the reference to the file
            processed_file = f"{dir_processed}null_data.csv"
            data.to_csv(processed_file, index=False)
            return processed_file
        
        # SORT DATA BY CREATED_DATE
        @task
        def sorted_data(data):
            data = pd.read_csv(data)
            data["at"] = pd.to_datetime(data["at"], errors="coerce")
            data = data.sort_values("at", ascending=False)
            # because of the OOM, created the reference to the file
            processed_file = f"{dir_processed}sorted_data.csv"
            data.to_csv(processed_file, index=False)
            return processed_file

        # REMOVE ALL UNNECESSARY CHARACTERS FROM THE "CONTENT" COLUMN, LEAVING ONLY TEXT AND PUNCTUATION
        @task(outlets=[Asset("/usr/local/airflow/include/processed/clean_data.csv")])
        def clean_data(data):
            data = pd.read_csv(data)
            data["content"] = data["content"].astype(str).str.replace(r"[^a-zA-Z\s\.\,\!\?\']", "", regex=True).str.strip()
            # because of the OOM, created the reference to the file
            processed_file = f"{dir_processed}clean_data.csv"
            data.to_csv(processed_file, index=False)
            return processed_file
        
        # TASK GROUP DEPENDENCIES
        return clean_data(sorted_data(null_data(data)))


    # DEPENDENCIES
    branch_check = check_branch_file()
    read = read_file()
    group = data_explore(read)

    wait_for_file >> branch_check
    branch_check >> [read, empty_file()]
    read >> group
  
wait_for_dataset()