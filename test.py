import yfinance as yf
import datetime
from zoneinfo import ZoneInfo
import database
import alert_service

now = datetime.datetime(2024, 10, 29, 14, 45, tzinfo=ZoneInfo("Europe/Paris"))

alert = {
    "_id": "12344",
    "symbol": "HO.PA",
    "direction": "up",
    "value": 151
}

db = database.get_database()
database.delete_all_notifications(db)
alert_service.handle_symbol_alerts('HO.PA', [alert], now, db)