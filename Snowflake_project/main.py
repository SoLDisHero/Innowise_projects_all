from snowflake.snowpark import Session
import pandas as pd

# remove the first index/column from the dataset

data = pd.read_csv("include/datasets/Airline_Dataset.csv").iloc[:, 1:]
data.to_csv("include/datasets/Airline_Dataset_new.csv", index=False)
