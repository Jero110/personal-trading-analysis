import requests
import plotly.graph_objs as go
from datetime import datetime

def fetch_and_plot_btc_prices():
    # Fetch data from Alpha Vantage API
    url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_MONTHLY&symbol=BTC&market=EUR&apikey=demo'
    response = requests.get(url)
    data = response.json()
    
    # Extract time series data
    time_series = data.get('Time Series (Digital Currency Monthly)', {})
    
    # Prepare data for plotting
    dates = []
    prices_high = []
    prices_low = []
    prices_close = []
    prices_open = []

    # Sort dates to ensure chronological order
    sorted_dates = sorted(time_series.keys())
    
    for date in sorted_dates:
        values = time_series[date]
        dates.append(datetime.strptime(date, '%Y-%m-%d'))
        prices_high.append(float(values['2. high']))
        prices_low.append(float(values['3. low']))
        prices_close.append(float(values['4. close']))
        prices_open.append(float(values['1. open']))

    # Create traces for the plot
    trace_high = go.Scatter(
        x=dates,
        y=prices_high,
        name='High',
        line=dict(color='#17BECF'),
        opacity=0.7
    )

    trace_low = go.Scatter(
        x=dates,
        y=prices_low,
        name='Low',
        line=dict(color='#7F7F7F'),
        opacity=0.7
    )

    trace_close = go.Scatter(
        x=dates,
        y=prices_close,
        name='Close',
        line=dict(color='#FD7E14'),
        opacity=0.9
    )

    trace_open = go.Scatter(
        x=dates,
        y=prices_open,
        name='Open',
        line=dict(color='#2E8B57'),
        opacity=0.7
    )

    # Create the layout with improved styling
    layout = go.Layout(
        title={
            'text': 'Bitcoin Price History (EUR)',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(
            title='Date',
            gridcolor='lightgrey',
            showgrid=True
        ),
        yaxis=dict(
            title='Price (EUR)',
            gridcolor='lightgrey',
            showgrid=True
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='lightgrey',
            borderwidth=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    # Create and show the figure
    fig = go.Figure(data=[trace_open, trace_high, trace_low, trace_close], layout=layout)
    
    # Add range selector buttons
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    fig.show()

# Run the function
fetch_and_plot_btc_prices()