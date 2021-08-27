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
        entry_points=[CommandHandler('start', TradingBot().start)],
        # different conversation steps and handlers that should be used if user sends a message
        # when conversation with them is currently in that state
        states={
            TradingBot.ID: [MessageHandler(Filters.text & ~Filters.regex('^/'), TradingBot().get_client_id)],
            TradingBot.SECRET: [MessageHandler(Filters.text & ~Filters.regex('^/'), TradingBot().get_client_secret)],
            TradingBot.TYPE: [
                MessageHandler(
                    Filters.regex('^(Stock|stock|Bond|bond|Fund|fund|ETF|etf|Warrant|warrant)$') & ~Filters.regex('^/'),
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

    moon_handler = CommandHandler('moon', TradingBot().to_the_moon)
    portfolio_handler = CommandHandler('portfolio', TradingBot().show_portfolio)

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(moon_handler)
    dispatcher.add_handler(portfolio_handler)

    # Start the Bot
    updater.start_polling()

    # Run the Bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
