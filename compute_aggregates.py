import database
from itertools import groupby
import yfinance as yf
import alert_service

aggregate_duration = '2y'
aggregate_days = 200


db = database.get_database()
all_alerts = database.get_all_alerts(db)
database.delete_all_aggregates(db)

def compute_aggregate(data, indicator):
    if indicator == 'mean_price_ratio':
        serie = data['Close']
    elif indicator == 'mean_volume_ratio':
        serie = data['Volume']
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
        if indicator in alert_service.indicator_types:
            value = compute_aggregate(data, indicator)
            aggregates.append({
                'symbol': symbol,
                'indicator': indicator,
                'value': value
            })
        else:
            id = next((alert['_id'] for alert in alerts if alert['indicator'] == indicator), None)
            print(f'Alert {id}: Unknown indicator {indicator}')

database.save_aggregates(db, aggregates)

print('Done !')