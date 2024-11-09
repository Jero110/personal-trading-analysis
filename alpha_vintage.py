import requests
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime

def fetch_crypto_data(timeframe='DAILY'):
    url = f'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_{timeframe}&symbol=BTC&market=EUR&apikey=demo'
    response = requests.get(url)
    return response.json()

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

def create_advanced_chart():
    # Fetch data from different timeframes
    daily_data = fetch_crypto_data('DAILY')
    
    # Create figure with secondary y-axis for volume
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3]
    )

    # Process daily data
    dates, opens, highs, lows, closes, volumes = process_data(daily_data, 'Daily')

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name='OHLC',
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350',
            increasing_fillcolor='#26A69A',
            decreasing_fillcolor='#EF5350'
        ),
        row=1, col=1
    )

    # Add volume bars
    colors = ['#26A69A' if closes[i] >= opens[i] else '#EF5350' for i in range(len(closes))]
    
    fig.add_trace(
        go.Bar(
            x=dates,
            y=volumes,
            name='Volume',
            marker_color=colors,
            opacity=0.5
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        title={
            'text': 'Bitcoin/EUR Price',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title='Price (EUR)',
        yaxis2_title='Volume',
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        xaxis_rangeslider_visible=False
    )

    # Update axes
    fig.update_xaxes(
        gridcolor='lightgrey',
        showgrid=True,
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1D", step="day", stepmode="backward"),
                dict(count=7, label="1W", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    fig.update_yaxes(
        gridcolor='lightgrey',
        showgrid=True,
        row=1, col=1
    )

    fig.update_yaxes(
        gridcolor='lightgrey',
        showgrid=True,
        row=2, col=1
    )

    # Update the style to match TradingView
    fig.update_layout(
        font=dict(
            family="Trebuchet MS, Arial, sans-serif",
            size=10,
            color="#333333"
        ),
        dragmode='zoom',
        selectdirection='h',
        showlegend=False
    )

    return fig

# Create and display the chart
fig = create_advanced_chart()
fig.show()