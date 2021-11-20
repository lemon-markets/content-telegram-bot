import logging
import os
from dotenv import load_dotenv

from models.TradingBot import TradingBot

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv()
    """Start the bot."""
    # Create the Updater and pass it to your bot's token.
    updater = Updater(os.getenv('BOT_TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        # initiate the conversation
        entry_points=[CommandHandler('trade', TradingBot().trade)],
        # different conversation steps and handlers that should be used if user sends a message
        # when conversation with them is currently in that state
        states={
            TradingBot.SPACE: [MessageHandler(Filters.text & ~Filters.regex('^/'), TradingBot().get_type)],
            TradingBot.TYPE: [MessageHandler(Filters.regex('^(Stock|stock|ETF|etf)$') & ~Filters.regex('^/'),
                                             TradingBot().get_search_query)],
            TradingBot.REPLY: [MessageHandler(Filters.text & ~Filters.regex('^/'), TradingBot().get_instrument_name)],
            TradingBot.NAME: [MessageHandler(Filters.text & ~Filters.regex('^/'), TradingBot().get_isin)],
            TradingBot.ISIN: [MessageHandler(Filters.text & ~Filters.regex('^/'), TradingBot().get_side)],
            TradingBot.SIDE: [MessageHandler(Filters.text & ~Filters.regex('^/'), TradingBot().get_quantity)],
            TradingBot.QUANTITY: [MessageHandler(Filters.text & ~Filters.regex('^/'), TradingBot().confirm_order)],
            TradingBot.CONFIRMATION: [MessageHandler(Filters.text, TradingBot().complete_order)]
        },
        # if user currently in conversation but state has no handler or handle inappropriate for update
        fallbacks=[CommandHandler(('cancel', 'end'), TradingBot().cancel)],
    )

    # quick_conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('quicktrade', TradingBot().quick_trade, pass_args=True)],
    #     states={
    #         TradingBot.QUICK: [MessageHandler(Filters.text & ~Filters.regex('^/'), TradingBot().confirm_quicktrade)],
    #     },
    #     fallbacks=[CommandHandler('cancel', TradingBot().cancel)]
    # )

    portfolio_handler = ConversationHandler(
        entry_points=[CommandHandler('portfolio', TradingBot().get_space, pass_args=True)],
        states={
            TradingBot.PORTFOLIO: [MessageHandler(Filters.text & ~Filters.regex('^/'), TradingBot().show_portfolio)],
        },
        fallbacks=[CommandHandler('cancel', TradingBot().cancel)]
    )
    start_handler = CommandHandler('start', TradingBot().start)
    moon_handler = CommandHandler('moon', TradingBot().to_the_moon)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(moon_handler)
    dispatcher.add_handler(portfolio_handler)

    # Start the Bot
    updater.start_polling()

    # Run the Bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
