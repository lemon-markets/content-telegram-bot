from helpers import RequestHandler


class Positions(RequestHandler):

    def get_positions(self):
        endpoint = 'positions/'
        response = self.get_data_trading(endpoint)
        return response['results']

