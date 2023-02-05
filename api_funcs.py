import requests
import configparser
import os
import pandas as pd


class connectAPI:
    def __init__(self, API, schema):
        config = configparser.ConfigParser()
        config.read(os.path.dirname(__file__) + "/conf_api.ini")
        self.url = config.get(API, "url")
        self.info = config.get(API, "info")
        self.header = {"content-type": "application/json"}
        self.attribute = schema

    def pages2list(self):
        response = requests.get(self.endpoint + f"?page=1").json()
        lst_results = response["results"]
        print(f"connected to {self.endpoint}")
        if eval(self.info):
            while response["info"]["next"]:
                response = requests.get(response["info"]["next"]).json()
                lst_results.extend(response["results"])
        else:
            while response["next"]:
                response = requests.get(response["next"]).json()
                lst_results.extend(response["results"])

        return lst_results

    def get_results_df(self):
        self.endpoint = self.url + self.attribute
        lst = self.pages2list()
        return pd.DataFrame(lst)
