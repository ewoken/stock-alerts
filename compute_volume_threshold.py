from database import Database
import yfinance as yf

detection_volume_quantile = 0.98 # -> ~5x/an

db = Database()
all_volume_alerts = db.get_all_volume_alerts()

for i, alert in enumerate(all_volume_alerts):
    symbol = alert['symbol']
    print(f'{i+1}/{len(all_volume_alerts)} - {symbol}')
    stock = yf.Ticker(symbol)
    data = stock.history(period='5y')
    threshold = data['Volume'].quantile(detection_volume_quantile)
    db.update_volume_alert(alert['_id'], threshold)

print('Done !')