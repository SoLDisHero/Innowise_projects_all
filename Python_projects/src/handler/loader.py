import json

# Since we use 3-4 sql,json files, we create class Loader for loading data from the data folder

class Loader:
    def __init__(self, path):
        self.path = path

    def load_json(self):
        with open(self.path, "r") as file:
            return json.load(file)
        
    def load_sql(self):
        with open(self.path, "r") as file:
            return file.read()