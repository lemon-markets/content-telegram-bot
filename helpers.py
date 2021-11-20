import os
import json
import requests


class RequestHandler:

    def __init__(self):
        self.api_key: str = os.environ.get("API_KEY")
        self.url_trading: str = os.environ.get("BASE_URL_TRADING")
        self.url_market: str = os.environ.get("BASE_URL_DATA")

    def get_data_trading(self, endpoint: str):
        response = requests.get(self.url_trading + endpoint, headers=self.headers)
        return response.json()

    def get_data_market(self, endpoint: str):
        response = requests.get(self.url_market + endpoint, headers=self.headers)
        return response.json()

    def post_data(self, endpoint: str, data):
        response = requests.post(self.url_trading + endpoint,
                                 json.dumps(data),
                                 headers=self.headers)
        return response.json()

    def delete_data(self, endpoint: str):
        response = requests.delete(self.url_trading + endpoint, headers=self.headers)
        return response.json()

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}