from alert_service import get_link
from database import Database
import yfinance as yf
import telegram

db = Database()
all_volume_alerts = db.get_all_volume_alerts()

for i, alert in enumerate(all_volume_alerts):
    symbol = alert['symbol']
    print(f'{i+1}/{len(all_volume_alerts)} - {symbol}')
    stock = yf.Ticker(symbol)
    data = stock.history(period='5d') # can be optimized

    if data.empty:
        continue

    last_volume = data['Volume'].iloc[-1]
    # last_growth = data['Close'].pct_change().iloc[-1]
    
    if last_volume > alert['value']: # and last_growth > 0:
        message = f'Volume on [{symbol}]({get_link(symbol)}) is high !'
        telegram.send_message(message, {
            "no_webpage": True,
            "parse_mode": "Markdown",
            "link_preview_options": { "is_disabled": True }
        })   


print('Done !')