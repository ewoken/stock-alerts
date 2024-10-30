from database import Database
from itertools import groupby
import yfinance as yf
from alert_service import AlertService, indicator_types

aggregate_duration = '2y'
aggregate_days = 200


db = Database()
alert_service = AlertService(db)
all_alerts = db.get_all_alerts()
db.delete_all_aggregates()

def compute_aggregate(data, indicator):
    if indicator == 'mean_price_ratio':
        serie = data['Close']
    else:
        raise ValueError(f'Unknown indicator {indicator}')
    
    return serie.rolling(window=aggregate_days).mean().iloc[-1]

aggregates = []
for symbol, alerts in groupby(all_alerts, lambda x: x['symbol']):
    stock = yf.Ticker(symbol)
    data = stock.history(
        period=aggregate_duration,
    ).sort_index()
    if data.empty:
        continue

    all_indicators = set([ alert['indicator'] for alert in alerts ])

    for indicator in all_indicators:
        if indicator == 'price':
            continue
        if indicator in indicator_types:
            value = compute_aggregate(data, indicator)
            aggregates.append({
                'symbol': symbol,
                'indicator': indicator,
                'value': value
            })
        else:
            id = next((alert['_id'] for alert in alerts if alert['indicator'] == indicator), None)
            print(f'Alert {id}: Unknown indicator {indicator}')

db.save_aggregates(aggregates)

print('Done !')