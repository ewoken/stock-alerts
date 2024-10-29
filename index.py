import datetime
from zoneinfo import ZoneInfo
import os
import requests
import yfinance as yf
from pymongo.mongo_client import MongoClient

now = datetime.datetime.now(tz=ZoneInfo("Europe/Paris"))
MONGO_URI = os.getenv("MONGO_URI")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

mongo = MongoClient(MONGO_URI)
db = mongo['stock-alerts-app']
stockAlertsCollection = db['stock-alerts']

def send_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    })

all_alerts = stockAlertsCollection.find({}).to_list(None)

if now.hour == 9 and now.minute < 5:
    send_message(f'Good morning ! {len(all_alerts)} alerts registered')

for alert in all_alerts:
    print(alert)

print('Done !')