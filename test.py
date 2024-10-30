import yfinance as yf
import datetime
from zoneinfo import ZoneInfo
from database import Database
from alert_service import AlertService

now = datetime.datetime(2024, 10, 29, 14, 45, tzinfo=ZoneInfo("Europe/Paris"))

alert = {
    "_id": "12344",
    "symbol": "HO.PA",
    "indicator": "price",
    "direction": "up",
    "value": 151
}

mean_price_alert = {
    "_id": "12345",
    "symbol": "HO.PA",
    "indicator": "mean_price_ratio",
    "direction": "up",
    "value": 1.006
}

database = Database()
alert_service = AlertService(database)
alert_service.handle_symbol_alerts([alert, mean_price_alert], { "mean_price_ratio": 150 }, now)