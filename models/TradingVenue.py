import datetime
import os

from helpers import RequestHandler


class TradingVenue(RequestHandler):

    def is_open(self) -> bool:
        mic: str = os.environ.get("MIC")
        endpoint = f'venues/?mic={mic}'
        response = self.get_data_market(endpoint)
        return response['results'][0]['is_open']

    def get_next_opening_time(self):
        mic: str = os.environ.get("MIC")
        endpoint = f'venues/?mic={mic}'
        response = self.get_data_market(endpoint)
        return response['results'][0]['opening_hours']['start']

    def get_next_opening_day(self):
        mic: str = os.environ.get("MIC")
        endpoint = f'venues/?mic={mic}'
        response = self.get_data_market(endpoint)
        return response['results'][0]['opening_days'][0]
