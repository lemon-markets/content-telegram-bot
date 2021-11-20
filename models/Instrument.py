import os
import random

from helpers import RequestHandler


class Instrument(RequestHandler):

    def get_titles(self, search_query: str, instrument_type: str):
        mic = os.getenv("MIC")
        endpoint = f'instruments/?search={search_query}&type={instrument_type}&mic={mic}'
        response = self.get_data_market(endpoint)
        results = response['results']

        instruments: dict = {}

        if len(results) <= 3:
            for result in results:
                instruments[result['title']] = result['isin']
        else:
            for result in results[:4]:
                instruments[result['title']] = result['isin']

        return instruments

    def get_title(self, isin: str):
        mic = os.getenv("MIC")
        endpoint = f'instruments/?isin={isin}&mic={mic}'
        response = self.get_data_market(endpoint)

        return response['results'][0]['title']

    def get_price(self, isin: str):
        mic = os.getenv("MIC")
        endpoint = f'quotes/?from=latest&mic={mic}&isin={isin}'
        response = self.get_data_market(endpoint)
        print(response)
        bid = response['results'][0]['b']
        ask = response['results'][0]['a']
        return bid, ask

    def get_quick_isin(self, search_query: str, instrument_type: str):
        endpoint = f'instruments/?search={search_query}&type={instrument_type}'
        return self.get_data_market(endpoint)['results'][0]

    def get_memes(self):
        # GME, BB, CLOV, AMC, PLTR, WISH, NIO, TSLA, Tilray, NOK
        memes = ['US36467W1099', 'CA09228F1036', 'US18914F1030', 'US00165C1045', 'US69608A1088', 'US21077C1071',
                 'US62914V1061', 'US88160R1014', 'US88688T1007', 'FI0009000681']
        endpoint = f'instruments/?type=stock&isin={random.choice(memes)}'
        response = self.get_data_market(endpoint)
        return response['results'][0]['title']
