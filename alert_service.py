import datetime
import yfinance as yf
import telegram
from database import Database

indicator_types = [
    "price",
    'mean_price_ratio',
]

# data from yfinance is available with a delay of 15 minutes
def is_first_run_of_day(now):
    return now.hour == 9 and now.minute < 10

def get_link(symbol):
    if symbol.endswith('.PA'):
        s = symbol.split('.')[0]
        return f'https://www.tradingview.com/symbols/EURONEXT-{s}/'
    return symbol


class AlertService:

    def __init__(self, db: Database):
        self.db = db

    def send_message_alert(self, alert_id, date, message):
        print(f'{alert_id} detected at {date}')
        date_fmt = datetime.datetime.strftime(date, "%H:%M")
        fmt_message = f'{date_fmt}, {message}'
        
        if not self.db.has_already_notif_today(alert_id):
            telegram.send_message(fmt_message, {
                "no_webpage": True,
                "parse_mode": "Markdown",
                "link_preview_options": { "is_disabled": True }
            })
            self.db.save_notification(alert_id)

    def detect_price_alert(self, alert, data):
        print(f'Computing alert {alert["_id"]}')
        if alert['direction'] == 'up':
            detected = (data['LastPrice'] < alert['value']) & (data['High'] >= alert['value'])
        elif alert['direction'] == 'down':
            detected = (data['LastPrice'] > alert['value']) & (data['Low'] <= alert['value'])
        else:
            raise ValueError('Invalid direction')

        if detected.any():
            date = detected.idxmax()
            symbol = alert['symbol']
            message = f'[{symbol}]({get_link(symbol)}) price is {alert["direction"]}: {alert["value"]}'
            self.send_message_alert(alert['_id'], date, message)

    def detect_mean_price_ratio_alert(self, alert, data, mean_price_value):
        print(f'Computing alert {alert["_id"]}')
        last_price_ratio = data['LastPrice'] / mean_price_value
        high_price_ratio = data['High'] / mean_price_value
        low_price_ratio = data['Low'] / mean_price_value

        print(last_price_ratio)
        print(high_price_ratio)

        if alert['direction'] == 'up':
            detected = (last_price_ratio < alert['value']) & (high_price_ratio >= alert['value'])
        elif alert['direction'] == 'down':
            detected = (last_price_ratio > alert['value']) & (low_price_ratio <= alert['value'])
        else:
            raise ValueError('Invalid direction')
        
        if detected.any():
            date = detected.idxmax()
            symbol = alert['symbol']
            message = f'[{symbol}]({get_link(symbol)}) price ratio is {alert["direction"]}: {alert["value"]}'
            self.send_message_alert(alert['_id'], date, message)

    def handle_symbol_alerts(self, alerts, aggregates, now):
        symbol = alerts[0]['symbol']
        is_first = is_first_run_of_day(now)
        stock = yf.Ticker(symbol)
        data = stock.history(
            start=now - datetime.timedelta(minutes=35), # should be 25 but add a margin
            end=now - datetime.timedelta(minutes=5), # should be 15 but add a margin
            interval='1m'
        ).sort_index()
        if data.empty:
            return
        data['LastPrice'] = data['Close'].shift(1)

        if (is_first):
            last_day_data = stock.history(period='1d').sort_index()
            last_price = last_day_data['Close'].iloc[-1]
            data.at[data.index[0], 'LastPrice'] = last_price

        for alert in alerts:
            if alert['indicator'] == 'price':
                self.detect_price_alert(alert, data)
            elif alert['indicator'] == 'mean_price_ratio':
                if 'mean_price_ratio' not in aggregates:
                    raise ValueError('mean_price_ratio not computed')
                self.detect_mean_price_ratio_alert(alert, data, aggregates['mean_price_ratio'])
            else:
                raise ValueError(f'Unknown indicator {alert["indicator"]}')


