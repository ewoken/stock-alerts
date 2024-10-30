import datetime
from zoneinfo import ZoneInfo
import yfinance as yf
from itertools import groupby
from alert_service import AlertService, is_first_run_of_day
from database import Database
import telegram

now = datetime.datetime.now(tz=ZoneInfo("Europe/Paris"))
is_first = is_first_run_of_day(now)

print(f'Running at {now}')

# data from yfinance is available with a delay of 15 minutes
if (now.hour < 9 or now.hour > 17 or 
    (now.hour == 9 and now.minute < 15) or
    (now.hour == 17 and now.minute > 55)): # should be 50 but add a margin
    print("Market is closed")
    exit()

db = Database()
alert_service = AlertService(db)
all_alerts = db.get_all_alerts(db)

if is_first:
    telegram.send_message(f'Good morning ! {len(all_alerts)} alerts registered')
    db.delete_all_notifications()

for symbol, alerts in groupby(all_alerts, lambda x: x['symbol']):
    alert_service.handle_symbol_alerts(list(alerts), now)

print('Done !')