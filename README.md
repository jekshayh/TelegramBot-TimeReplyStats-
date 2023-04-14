# TelegramBot-TimeReplyStats-

Telegram Bot for tracking and visualizing curators' response time.

The bot can track the time it takes for a curator to respond to a question and generate visualized statistics on the average response time for each curator.

Getting Started

To use this bot, you will need to do the following:

Install the required dependencies by running pip install aiogram matplotlib sqlite3.
Create a new Telegram bot by talking to the BotFather and obtaining a unique API token and then adding it to the API_TOKEN = 'place your token here' line.
To start the bot, run the bot.py file.

Usage

Before collecting data curators can be registered to the bot's database via sending "/future_password" command.

Once the bot is running it will be collecting users' questions and curators' answers/replies in a chat.

To see statistics on the average response time for each curator, a curator can send the message "stats", it also can be done in direct messages to the bot. The bot will then generate a bar graph showing the average response time for each curator in minutes.
