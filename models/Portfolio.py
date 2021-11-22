from helpers import RequestHandler


class Portfolio(RequestHandler):

    def get_portfolio(self, space_id: str):
        endpoint = f'portfolio/?space_id={space_id}'
        response = self.get_data_trading(endpoint)
        return response['results']

