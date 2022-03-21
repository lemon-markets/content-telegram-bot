from helpers import RequestHandler


class Account(RequestHandler):

    def get_balance(self):
        endpoint = 'account/'

        response = self.get_data_trading(endpoint)
        return response['results']['cash_to_invest']
