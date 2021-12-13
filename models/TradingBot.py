import datetime
import time

import dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

from models.Instrument import Instrument
from models.Order import Order
from models.Portfolio import Portfolio
from models.Space import Space
from models.TradingVenue import TradingVenue


class TradingBot:
    TYPE, ID, SECRET, SPACE, REPLY, NAME, ISIN, SIDE, QUANTITY, CONFIRMATION, PORTFOLIO, QUICK, QUICKTRADE = range(13)

    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)

    def start(self, update: Update, context: CallbackContext) -> int:
        """Initiates conversation."""
        context.chat_data.clear()
        context.user_data.clear()

        # collect user's name
        user = update.message.from_user.name

        # if Trading Venue closed, indicate next opening time and end conversation
        if not TradingVenue().is_open():
            opening_date: str = TradingVenue().get_next_opening_day()
            opening_time: str = TradingVenue().get_next_opening_time()
            update.message.reply_text(
                f'This exchange is closed at the moment. Please try again on {opening_date} at {opening_time}.'
            )
            return ConversationHandler.END

        update.message.reply_text(
            f'Hi {user}! I\'m the Lemon Trader Bot! I can place trades for you using the lemon.markets API. '
            'You can control me by sending or clicking on these commands:\n\n'

            'Regular Commands (no input required):\n'
            '/trade - place trade\n'
            '/quicktrade - place shortform trade\n'
            '/portfolio - list your portfolio\n'
            '/moon - meme stock generator\n'
        )

        print("Conversation started.")
        print(context.chat_data)

    def trade(self, update: Update, context: CallbackContext) -> int:
        """Initiates trade sequence."""
        context.chat_data.clear()
        context.user_data.clear()

        print(f'chat_data {context.chat_data}')

        context.user_data['spaces_ids'] = Space().get_spaces()

        spaces = list(context.user_data['spaces_ids'].keys())
        reply_keyboard = [spaces]

        update.message.reply_text(
            'Please select a Space.',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
            ),
        )
        return TradingBot.SPACE

    def quick_trade(self, update: Update, context: CallbackContext) -> int:
        """Initiates quick trade sequence."""
        context.chat_data.clear()
        context.user_data['space_id_quicktrade'] = context.user_data['spaces_ids'].get(update.message.text)

        update.message.reply_text(
            'Please specify your quick trade in the following format: \'buy 5 apple stock\''
        )
        return TradingBot.QUICKTRADE

    def perform_quicktrade(self, update: Update, context: CallbackContext) -> int:
        """Places quicktrade order."""
        trade_elements = update.message.text.split(' ')

        if len(trade_elements) != 4:
            update.message.reply_text(
                'A quick trade must be placed in the following format: \'/quicktrade buy 5 apple stock\''
            )
            return ConversationHandler.END
        else:
            try:
                side = trade_elements[0].lower()
                quantity = int(trade_elements[1])
                search = trade_elements[2].lower()
                if trade_elements[3].lower().startswith('share'):
                    instrument_type = 'stock'
                else:
                    instrument_type = trade_elements[3].lower()

                instrument = Instrument().get_quick_isin(search, instrument_type)

                context.chat_data['order'] = Order().place_order(instrument['isin'],
                                                                 "p0d",
                                                                 quantity,
                                                                 side,
                                                                 context.user_data['space_id_quicktrade'])
                [context.chat_data['bid'], context.chat_data['ask']] = Instrument().get_price(instrument['isin'])
                reply_keyboard = [['Confirm', 'Cancel']]

                if side == 'buy':
                    price = round(context.chat_data['ask'], 2)

                else:
                    price = round(context.chat_data['bid'], 2)

                update.message.reply_text(
                    f'You indicated that you wish to {side} {quantity} {instrument.get("title")} {instrument_type} at €{price} per share. Is that '
                    f'correct?',
                    reply_markup=ReplyKeyboardMarkup(
                        reply_keyboard, one_time_keyboard=True,
                    ),
                )
                return TradingBot.QUICK

            except Exception as e:
                print(e)
                update.message.reply_text(
                    "There was an error, ending conversation.")
                return ConversationHandler.END

    def confirm_quicktrade(self, update: Update, context: CallbackContext) -> int:
        """Activates quicktrade order."""
        reply = update.message.text
        if reply == 'Confirm':
            if context.chat_data['order']['status'] == 'error':
                update.message.reply_text(
                    "Insufficient holdings, ending conversation"
                )
                return ConversationHandler.END
            try:
                print(context.chat_data)
                order = Order().activate_order(context.chat_data['order']['results'].get('id'))
                update.message.reply_text(
                    "Please wait while we process your order."
                )
                start = datetime.datetime.now()
                while True and len(context.chat_data['order']) > 1:

                    order_summary = Order().get_order(
                        context.chat_data['order']['results'].get('id')
                    )
                    # need to check here if the order is actually placed, so maybe check length of 'order'
                    if order_summary['results'].get('status') == 'executed':
                        context.chat_data['average_price'] = order_summary['results'].get('executed_price')
                        print('executed')
                        break
                    elif datetime.datetime.now() - start >= datetime.timedelta(minutes=3):
                        update.message.reply_text(
                            'We\'re currently experiencing some delays. Your order was not executed. Please try again '
                            'later. '
                        )
                        # delete all inactive orders
                        Order().delete_order(context.user_data['space_id_quicktrade'])
                        return ConversationHandler.END
                    time.sleep(2)

                update.message.reply_text(
                    f'Your order was executed at €{context.chat_data["average_price"]/10000:,.2f} per share. '
                )
                return ConversationHandler.END

            except Exception as e:
                print(e)
                update.message.reply_text(
                    "There was an error, ending conversation.")
                return ConversationHandler.END
        elif reply == 'Cancel':
            update.message.reply_text(
                "You cancelled the order. Ending conversation.")

            return ConversationHandler.END
        else:
            update.message.reply_text(
                "There was an error, ending conversation.")
            return ConversationHandler.END

    def get_type(self, update: Update, context: CallbackContext) -> int:
        """Retrieves financial instrument type."""
        context.user_data['space_id'] = context.user_data['spaces_ids'].get(update.message.text)

        reply_keyboard = [['Stock', 'ETF']]

        print(f'chat_data {context.chat_data}')

        update.message.reply_text(
            'What type of instrument do you want to trade?',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
            ),
        )
        return TradingBot.TYPE

    def get_search_query(self, update: Update, context: CallbackContext) -> int:
        """Prompts user to enter instrument name."""
        # store user response in dictionary with key 'type'
        context.chat_data['type'] = update.message.text.lower()

        print(f'chat_data {context.chat_data}')

        update.message.reply_text(
            f'What is the name of the {context.chat_data["type"]} you would like to trade?')

        return TradingBot.REPLY

    def get_instrument_name(self, update: Update, context: CallbackContext) -> int:
        """Searches for instrument and prompts user to select an instrument."""
        context.chat_data['search_query'] = update.message.text.lower()

        print(f'chat_data {context.chat_data}')

        try:
            instruments = Instrument().get_titles(context.chat_data['search_query'],
                                                  context.chat_data['type'])
        except Exception as e:
            print(e)
            update.message.reply_text(
                "There was an error, ending the conversation. If you'd like to try again, send /start.")
            return ConversationHandler.END

        titles = list(instruments.keys())
        titles.append('Other')

        reply_keyboard = [titles]

        update.message.reply_text(
            f'Please choose the instrument you wish to trade. If you do not see the desired instrument, press "Other".',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
            ),
        )
        return TradingBot.NAME

    def get_isin(self, update: Update, context: CallbackContext) -> int:
        """Retrieves ISIN and prompts user to select side (buy/sell)."""
        text = update.message.text

        try:
            instruments = Instrument().get_titles(context.chat_data['search_query'],
                                                  context.chat_data['type'])
        except Exception as e:
            print(e)
            update.message.reply_text(
                "There was an error, ending the conversation. If you'd like to try again, send /start.")
            return ConversationHandler.END

        if text == 'Other':
            update.message.reply_text("Please be more specific in your search query.")
            return TradingBot.REPLY

        # if user chooses name, find isin
        else:
            context.chat_data['title'] = text
            context.chat_data['isin'] = instruments.get(text)

            reply_keyboard = [['Buy', 'Sell']]
            update.message.reply_text(
                f'Would you like to buy or sell {context.chat_data["title"]}?',
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True,
                )
            )
            print(f'chat_data {context.chat_data}')

            return TradingBot.ISIN

    def get_side(self, update: Update, context: CallbackContext) -> int:
        """Retrieves total balance (buy) or amount of shares owned (sell), most recent price and prompts user to
        indicate quantity. """
        context.chat_data['side'] = update.message.text.lower()
        try:
            [context.chat_data['bid'], context.chat_data['ask']] = Instrument().get_price(context.chat_data['isin'])
            context.chat_data['balance'] = Space().get_balance(context.user_data['space_id'])
        except Exception as e:
            print(e)
            update.message.reply_text(
                "There was an error, ending the conversation. If you'd like to try again, send /start.")
            return ConversationHandler.END

        # if user chooses buy, present ask price, total balance and ask how many to buy
        if context.chat_data['side'] == 'buy':
            update.message.reply_text(
                f'This instrument is currently trading for €{context.chat_data["ask"]}, your total balance is '
                f'€{context.chat_data["balance"] / 10000:,.2f}. '
                f'How many shares do you wish to {context.chat_data["side"]}?'
            )
        # if user chooses sell, retrieve how many shares owned
        else:
            positions = Portfolio().get_portfolio(context.user_data['space_id'])
            print(positions)
            # initialise shares owned to 0
            context.chat_data['shares_owned'] = 0

            # if instrument in portfolio, update shares owned
            if context.chat_data['isin'] in positions:
                context.chat_data['shares_owned'] = \
                    positions[context.chat_data['isin']][context.user_data['space_id']].get('quantity')

            update.message.reply_text(
                f'This instrument can be sold for €{round(context.chat_data["bid"], 2)}, you currently own '
                f'{context.chat_data["shares_owned"]} share(s). '
                f'How many shares do you wish to {context.chat_data["side"]}?'
            )

            print(f'chat_data {context.chat_data}')

        return TradingBot.SIDE

    def get_quantity(self, update: Update, context: CallbackContext) -> int:
        """Processes quantity (handles error if purchase/sale not possible), places order (if possible) and prompts
        user to confirm order. """
        context.chat_data['quantity'] = float(update.message.text.lower())

        reply_keyboard = [['Confirm', 'Cancel']]

        # if user indicates 0 to buy, then prompt to enter new amount or end current process
        if context.chat_data['quantity'] == 0:
            update.message.reply_text(
                'You have indicated you do not wish to buy any shares, type '
                '/cancel to abort this process or enter a new amount.'
            )
            return TradingBot.SIDE

        # determine total cost of buy or sell
        if context.chat_data['side'] == 'buy':
            context.chat_data['total'] = context.chat_data['quantity'] * float(context.chat_data['ask'])
        else:
            context.chat_data['total'] = context.chat_data['quantity'] * float(context.chat_data['bid'])

        # if buy and can't afford buy, prompt user to enter new amount
        if context.chat_data['side'] == 'buy' and context.chat_data['total'] > context.chat_data['balance'] / 10000:
            update.message.reply_text(
                f'You do not have enough money to buy {context.chat_data["quantity"]} of {context.chat_data["title"]}. '
                'Please enter a new amount.'
            )
            return TradingBot.SIDE

        # if sell and don't have that many shares, prompt user to enter new amount
        elif context.chat_data['side'] == 'sell' and context.chat_data['shares_owned'] < context.chat_data['quantity']:
            update.message.reply_text(
                f'You do not have enough shares of {context.chat_data["title"]} in your portfolio. '
                'Please enter a new amount.'
            )
            return TradingBot.SIDE

        # if quantity not an int, prompt user to enter new amount
        elif not context.chat_data['quantity'].is_integer():
            update.message.reply_text(
                'You\'ve entered an invalid amount. Please try again.'
            )
            return TradingBot.SIDE

        else:
            try:
                # place order
                context.chat_data['order_id'] = \
                    Order().place_order(
                        isin=context.chat_data['isin'],
                        expires_at="p0d",
                        side=context.chat_data['side'],
                        quantity=context.chat_data['quantity'],
                        space_id=context.user_data['space_id']
                    ).get('results')['id']
            except Exception as e:
                print(e)
                update.message.reply_text(
                    "There was an error, ending the conversation. If you'd like to try again, send /start.")
                return ConversationHandler.END

            update.message.reply_text(
                f'You\'ve indicated that you wish to {context.chat_data["side"]} {int(context.chat_data["quantity"])} '
                f'share(s) of {context.chat_data["title"]} at a total of €{round(context.chat_data["total"], 2)}. '
                f'Please confirm or cancel your order to continue.',
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True,
                )
            )
            print(f'chat_data {context.chat_data}')

            return TradingBot.QUANTITY

    def confirm_order(self, update: Update, context: CallbackContext) -> int:
        """Activates order (if applicable), displays purchase/sale price and prompts user to indicate whether any
        additional trades should be made. """
        context.chat_data['order_decision'] = update.message.text
        reply_keyboard = [['Yes', 'No']]

        if context.chat_data['order_decision'] == 'Cancel':
            update.message.reply_text(
                'You\'ve cancelled your order. Would you like to make another trade?',
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True,
                )
            )
        else:
            try:
                Order().activate_order(
                    context.chat_data['order_id'],
                )
            except Exception as e:
                print(e)
                update.message.reply_text(
                    "There was an error, ending the conversation. If you'd like to try again, send /start.")
                return ConversationHandler.END

            # keep checking order status until executed so that execution price can be retrieved
            update.message.reply_text(
                'Please wait while we process your order.'
            )
            while True:
                order_summary = Order().get_order(
                    context.chat_data['order_id'],
                )
                if order_summary['results'].get('status') == 'executed':
                    print('executed')
                    break
                time.sleep(2)

            context.chat_data['average_price'] = order_summary['results'].get('executed_price')

            update.message.reply_text(
                f'Your order was executed at €{context.chat_data["average_price"]/10000:,.2f} per share. '
                'Would you like to make another trade?',
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True
                )
            )
        print(f'chat_data {context.chat_data}')

        return TradingBot.CONFIRMATION

    def complete_order(self, update: Update, context: CallbackContext) -> int:
        """Prompts user to continue or end conversation."""
        if update.message.text == 'Yes':
            context.chat_data.clear()
            reply_keyboard = [['Stock', 'ETF']]
            update.message.reply_text(
                'What type of instrument do you want to trade?',
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True,
                ),
            )
            return TradingBot.TYPE
        else:
            update.message.reply_text(
                "Bye! Come back if you would like to make any other trades.", reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext) -> int:
        """Cancels and ends the conversation."""
        update.message.reply_text(
            "Bye! Come back if you would like to make any other trades.", reply_markup=ReplyKeyboardRemove()
        )
        print(f'chat_data {context.chat_data}')
        return ConversationHandler.END

    def to_the_moon(self, update: Update, context: CallbackContext):
        """Randomly prints a meme stock."""
        try:
            meme_stock = Instrument().get_memes()
        except Exception as e:
            print(e)
            update.message.reply_text(
                "There was an error, ending the conversation. If you'd like to try again, send /start.")
            return ConversationHandler.END

        update.message.reply_text(
            f'{meme_stock} to the moon 🚀'
        )

    def get_space(self, update: Update, context: CallbackContext):
        """Retrieves space for which to view portfolio."""

        context.chat_data['spaces_ids'] = Space().get_spaces()
        spaces = list(context.chat_data['spaces_ids'].keys())
        reply_keyboard = [spaces]

        update.message.reply_text(
            'For which Space would you like to view your portfolio?',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
            ),
        )
        return TradingBot.PORTFOLIO

    def show_portfolio(self, update: Update, context: CallbackContext):
        context.chat_data['space_id_portfolio'] = context.chat_data['spaces_ids'].get(update.message.text)

        try:
            portfolio = Portfolio().get_portfolio(context.chat_data['space_id_portfolio'])
            print(portfolio)
        except Exception as e:
            print(e)
            update.message.reply_text(
                "There was an error, ending the conversation. If you'd like to try again, send /start.")
            return ConversationHandler.END

        for isin, information in portfolio.items():
            name = Instrument().get_title(isin)
            quantity = information[context.chat_data["space_id_portfolio"]]["quantity"]
            average_price = information[context.chat_data["space_id_portfolio"]]["buy_price_avg"]
            if quantity != 0:
                update.message.reply_text(
                    f'Name: {name}\n'
                    f'Quantity: {quantity}\n'
                    f'Average Price: €{average_price/10000:,.2f}'
                )

        return ConversationHandler.END
