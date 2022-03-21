# from helpers import RequestHandler
#
#
# class Space(RequestHandler):
#
#     def get_spaces(self,):
#         endpoint = f'spaces'
#         results = self.get_data_trading(endpoint)['results']
#
#         spaces: dict = {}
#         for result in results:
#             spaces[result['name']] = result['id']
#
#         return spaces
#
#     def get_balance(self, space_id):
#         endpoint = f'spaces/{space_id}/'
#         response = self.get_data_trading(endpoint)
#         return response['results']['buying_power']
