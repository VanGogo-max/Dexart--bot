import json
import telebot
from tronapi import Tron
from tronapi.providers import HttpProvider

with open('config.json', 'r') as f:
    config = json.load(f)

bot = telebot.TeleBot(config['bot_token'])
tron = Tron(HttpProvider('https://api.trongrid.io'), HttpProvider('https://api.trongrid.io'))

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Welcome to DEXART!
Send /pay to purchase a license.")

@bot.message_handler(commands=['pay'])
def pay(message):
    bot.send_message(message.chat.id, f"Send 7 USDT (TRC-20) to:
{config['payment_address']}

Then send your TxID.")

@bot.message_handler(func=lambda m: len(m.text.strip()) == 64)
def check_tx(message):
    txid = message.text.strip()
    try:
        tx = tron.trx.get_transaction(txid)
        if tx['raw_data']['contract'][0]['parameter']['value']['to_address'][-40:].lower() == config['payment_address'][-40:].lower():
            if int(tx['raw_data']['contract'][0]['parameter']['value']['amount']) >= 7_000_000:
                user_id = str(message.chat.id)
                licenses = json.load(open("licenses.json", "r"))
                licenses[user_id] = "active"
                json.dump(licenses, open("licenses.json", "w"))
                bot.send_message(message.chat.id, "✅ License activated!")
                return
    except Exception as e:
        print(e)
    bot.send_message(message.chat.id, "❌ Invalid or insufficient transaction.")

bot.polling()