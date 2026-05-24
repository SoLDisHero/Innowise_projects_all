from airflow.sdk import dag, task, Asset
from pendulum import datetime
from airflow.providers.mongo.hooks.mongo import MongoHook

import pandas as pd

@dag(
    start_date=datetime(2026,1,1),
    schedule=[Asset("/usr/local/airflow/include/processed/clean_data.csv")],
    tags=['load','mongoDB'],
    description="Loading data into MongoDB",
    catchup=False
)
def loading_data():
    @task
    def load_to_mongo(asset_file="/usr/local/airflow/include/processed/clean_data.csv"):
        data = pd.read_csv(asset_file)
        converting_data = data.to_dict(orient="records")
        hook = MongoHook(mongo_conn_id="mongodb_default")
        client = hook.get_conn()

        db = client["tiktok"]
        collection = db["reviews"]
        # deleting collection if it exists
        collection.delete_many({})
        # inserting data into collection
        collection.insert_many(converting_data)
        
        # QUERY 1: Top 5 frequently occurring comments
        results_1 = collection.aggregate([{"$group": {"_id": "$content", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit":5}])
        for res in results_1:
            print(f"Comment: {res['_id']}, Count: {res['count']}")     

        # QUERY 2: All entries where the “content” field is less than 5 characters long
        results_2 = collection.find({"$where": "this.content.length < 5"}, {"content": 1, "_id": 0}).limit(20)
        for res in results_2:
            print(f"Comment: {res['content']}")

        # QUERY 3: Average rating for each day (the result should be in timestamp type)
        results_3 = collection.aggregate([{"$addFields": {"date": {"$dateTrunc": {"date": {"$toDate": "$at"}, "unit": "day"}}}},
                                         {"$group": {"_id": "$date", "avg_rating": {"$avg": "$score"}}},
                                         {"$sort": {"_id": 1}},
                                         {"$limit": 20}])
        for res in results_3:
            print(f"Date: {res['_id']}, Average_rating: {res['avg_rating']:.2f}")
                                          
        client.close()


    load_to_mongo()

loading_data()