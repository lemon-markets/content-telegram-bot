from helpers import RequestHandler


class Space(RequestHandler):

    def get_space_uuid(self,):
        endpoint = f'spaces'
        response = self.get_data_trading(endpoint)['results']
        return response[0]['uuid']

    def get_balance(self, space_uuid):
        endpoint = f'spaces/{space_uuid}/'
        response = self.get_data_trading(endpoint)
        return float(response['state']['cash_to_invest'])
