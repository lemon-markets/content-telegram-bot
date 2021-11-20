<h1 align="center">
  🤖 lemon.markets Telegram Bot
</h1>

> Note: This is not an official [lemon.markets](https://lemon.markets) bot. Please only use this as a starting point or reference for your own projects. 

## 🚀 What can it do? 


This Telegram bot is provided by lemon.markets to showcase one of the many use-cases of the API. This bot can be used to place trades on your own lemon.markets
account and gain an overview of your portfolio. The available commands are: `/start`, `/trade`, `/quicktrade`, `/portfolio` and `/moon`. 

If you'd like a step-by-step tutorial on this project, check out our YouTube video [here](https://www.youtube.com/watch?v=md64kPfxKg8) and our blog-post [here](https://medium.com/lemon-markets/setting-up-your-own-telegram-bot-to-trade-with-the-lemon-markets-api-part-1-of-2-98d7153bd5f6).

## 🛠️ Getting Set-Up


This repository requires the creation of an `.env` file with the following variables to communicate with the lemon.markets API: `MIC`, `API_KEY` 
`TRADING_URL` and `MARKET_URL`. It also needs a `BOT_TOKEN` to communicate with the Telegram API.

### 🍋 lemon.markets

There are two lemon.markets API URLs, one for trading and the other for market data. Please refer to the [documentation](https://docs.lemon.markets) to learn more and find the appropriate URLs. 

### 📞 Telegram

To connect to the Telegram API, you must obtain an access token by setting up a new bot via @BotFather. Read [this guide](https://core.telegram.org/bots#6-botfather)
to find out how. 

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (git checkout -b new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin new-feature)
5. Create a new Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

Copyright (c) 2021 Joanne Snel
