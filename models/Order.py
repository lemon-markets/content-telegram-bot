import os

from helpers import RequestHandler


class Order(RequestHandler):

    def place_order(self, isin: str, expires_at: str, quantity: int, side: str):
        order_details = {
            "isin": isin,
            "expires_at": expires_at,
            "side": side,
            "quantity": quantity,
            "venue": os.environ.get("MIC"),
        }
        endpoint = f'orders/'
        response = self.post_data(endpoint, order_details)
        return response

    def activate_order(self, order_id: str):
        endpoint = f'orders/{order_id}/activate/'
        response = self.post_data(endpoint, {})
        return response

    def get_order(self, order_id: str):
        endpoint = f'orders/{order_id}'
        response = self.get_data_trading(endpoint)
        return response

    def delete_order(self, order_id: str):
        endpoint = f'orders/{order_id}/'
        response = self.delete_data(endpoint)
        return response
