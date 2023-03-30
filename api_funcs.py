import requests
import configparser
import os
import pandas as pd


class connectAPI:
    def __init__(self, API, schema):
        # initialize connection to API
        config = configparser.ConfigParser()
        config.read(os.path.dirname(__file__) + "/conf_api.ini")
        self.url = config.get(API, "url")
        self.info = config.get(API, "info")
        self.token = config.get(API, "token")
        self.header = {"content-type": "application/json"}
        self.attribute = schema
        if self.token != "None":
            self.api_key = os.environ.get(self.token)

    def pages2list_tokenfree(self):
        # Collect pages from the token-free API endpoint and return a list of results
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

    def pages2list_token(self):
        # Collect pages from the API endpoint and return a list of results
        genders = {0: "Not Specified", 1: "Female", 2: "Male", 3: "Non-Binary"}
        n_people = 10_000
        self.endpoint = self.url + self.attribute
        print(f"Connecting to {self.endpoint}")
        gender_list = [
            {
                "gender": genders[response["gender"]],
                "n_credits": len(
                    requests.get(
                        f"{self.endpoint}/{i}/movie_credits",
                        params={"api_key": self.api_key, "language": "en_US"},
                    ).json()["cast"]
                ),
            }
            for i in range(1, n_people)
            if "gender"
            in (
                response := requests.get(
                    f"{self.endpoint}/{i}",
                    params={"api_key": self.api_key, "language": "en_US"},
                ).json()
            ).keys()
        ]

        return gender_list

    def get_results_df(self):
        self.endpoint = self.url + self.attribute
        if self.token == "None":
            lst = self.pages2list_tokenfree()
        elif self.token != "None":
            lst = self.pages2list_token()
        return pd.DataFrame(lst)
