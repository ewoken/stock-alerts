import datetime
from zoneinfo import ZoneInfo
import yfinance as yf
from itertools import groupby
import alerts
import database
import telegram

now = datetime.datetime.now(tz=ZoneInfo("Europe/Paris"))
is_first_run_of_day = alerts.is_first_run_of_day(now)

# data from yfinance is available with a delay of 15 minutes
if (now.hour < 9 or now.hour > 17 or 
    (now.hour == 9 and now.minute < 15) or
    (now.hour == 17 and now.minute > 50)):
    print("Market is closed")
    exit()

db = database.get_database()
all_alerts = database.get_all_alerts(db)

if is_first_run_of_day:
    telegram.send_message(f'Good morning ! {len(all_alerts)} alerts registered')
    database.delete_all_notifications(db)

for symbol, alerts in groupby(all_alerts, lambda x: x['symbol']):
    alerts.handle_symbol_alerts(symbol, list(alerts))

print('Done !')