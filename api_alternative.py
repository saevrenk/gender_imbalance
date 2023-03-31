import requests
import os
import configparser
import json
from typing import Optional
import pandas as pd


class APIConnector:
    def __init__(self, api_name: str, api_schema: str, token: Optional[str] = None):
        self.api_name = api_name
        self.api_schema = api_schema
        self.token = token

        config = configparser.ConfigParser()
        config.read(os.path.dirname(__file__) + "/conf_api.ini")
        self.url = config.get(self.api_name, "url")
        self.info = config.get(self.api_name, "info")
        self.header = {"content-type": "application/json"}

    def get_url(self, endpoint: str) -> str:
        return self.url + endpoint

    def get_token(self) -> Optional[str]:
        if self.token:
            return self.token
        else:
            return os.environ.get(self.api_name.upper() + "_API_KEY", None)

    def pages2list(self, endpoint: str):
        api_key = self.get_token()
        if api_key:
            return self.pages2list_token(endpoint, api_key)
        else:
            return self.pages2list_tokenfree(endpoint)

    def pages2list_token(self, endpoint: str, api_key: str):
        # Collect pages from the API endpoint and return a list of results
        lst_results = []
        n_people = 10_000
        g_dict = {0: "Not Specified", 1: "Female", 2: "Male", 3: "Non-Binary"}

        for i in range(1, n_people):
            url = self.get_url(endpoint) + "/" + str(i)
            response = requests.get(
                url, params={"api_key": api_key, "language": "en_US"}
            ).json()

            if "gender" in response.keys():
                res_movie_credits = requests.get(
                    url + "/movie_credits?",
                    params={"api_key": api_key, "language": "en_US"},
                ).json()
                lst_results.append(
                    {
                        "gender": g_dict[response["gender"]],
                        "n_credits": len(res_movie_credits["cast"]),
                    }
                )
        return lst_results

    def pages2list_tokenfree(self, endpoint: str):
        # Collect pages from the token-free API endpoint and return a list of results
        lst_results = []
        response = requests.get(self.get_url(endpoint) + f"?page=1").json()
        lst_results = response["results"]
        print(f"Connected to {self.get_url(endpoint)}")
        if eval(self.info):
            while response["info"]["next"]:
                response = requests.get(response["info"]["next"]).json()
                lst_results.extend(response["results"])
        else:
            while response["next"]:
                response = requests.get(response["next"]).json()
                lst_results.extend(response["results"])
        return lst_results

    def get_results_df(self, endpoint: str):
        lst = self.pages2list(endpoint)
        return pd.DataFrame(lst)
