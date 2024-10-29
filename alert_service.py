import datetime
import yfinance as yf
import telegram
import database

indicator_types = [
    "price",
    'mean_price_ratio',
    'mean_volume_ratio',
]

# data from yfinance is available with a delay of 15 minutes
def is_first_run_of_day(now):
    return now.hour == 9 and now.minute < 10

def send_message_alert(alert, date, db):
    alert_id = str(alert['_id'])
    print(f'{alert_id} detected at {date}')
    symbol = alert['symbol']
    message = f'{date}, [{symbol}]({get_link(symbol)}) price is {alert["direction"]}: {alert["value"]}'
    if (db is not None):
        if not database.has_already_notif_today(db, alert_id):
            telegram.send_message(message, {
                "no_webpage": True,
                "parse_mode": "Markdown",
                "link_preview_options": { "is_disabled": True }
            })
            database.save_notification(db, alert_id)

def detect_price_alert(alert, data, db):
    print(f'Computing alert {alert["_id"]}')
    if alert['direction'] == 'up':
        detected = (data['LastPrice'] < alert['value']) & (data['High'] >= alert['value'])
    elif alert['direction'] == 'down':
        detected = (data['LastPrice'] > alert['value']) & (data['Low'] <= alert['value'])
    else:
        raise ValueError('Invalid direction')

    if detected.any():
        idx = detected.idxmax()
        send_message_alert(alert, idx, db)

def handle_symbol_alerts(symbol, alerts, now, db=None):
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
            detect_price_alert(alert, data, db)


def get_link(symbol):
    if symbol.endswith('.PA'):
        s = symbol.split('.')[0]
        return f'https://www.tradingview.com/symbols/EURONEXT-{s}/'
    return symbol