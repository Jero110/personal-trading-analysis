from datetime import datetime

def process_data(data, timeframe):
    time_series_key = f'Time Series (Digital Currency {timeframe})'
    time_series = data.get(time_series_key, {})
    
    dates = []
    prices_open = []
    prices_high = []
    prices_low = []
    prices_close = []
    volumes = []

    sorted_dates = sorted(time_series.keys())
    
    for date in sorted_dates:
        values = time_series[date]
        dates.append(datetime.strptime(date, '%Y-%m-%d'))
        prices_open.append(float(values['1. open']))
        prices_high.append(float(values['2. high']))
        prices_low.append(float(values['3. low']))
        prices_close.append(float(values['4. close']))
        volumes.append(float(values['5. volume']))
    
    return dates, prices_open, prices_high, prices_low, prices_close, volumes
