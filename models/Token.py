import os

import requests


class Token():

    def __init__(self):
        self.auth_url: str = os.environ.get("AUTH_URL")

    def authenticate(self, client_id: str, client_secret: str):

        token_details = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        endpoint = f'oauth2/token/'
        response = self.get_token(endpoint, token_details)

        return response

    def get_token(self, endpoint: str, data):
        response = requests.post(self.auth_url + endpoint, data)
        return response.json()

