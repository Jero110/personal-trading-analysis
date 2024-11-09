import requests
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
import json
import time
import re
import os
from dotenv import load_dotenv

load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
def fetch_crypto_data(timeframe='DAILY'):
    url = f'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_{timeframe}&symbol=BTC&market=EUR&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)
    return response.json()

def process_data(data, timeframe, start_date=None, end_date=None):
    time_series_key = f'Time Series (Digital Currency {timeframe})'
    time_series = data.get(time_series_key, {})
    
    dates = []
    prices_open = []
    prices_high = []
    prices_low = []
    prices_close = []
    volumes = []
    colors = []
    
    # Split data for in-range and out-of-range periods
    in_range_data = {
        'dates': [], 'opens': [], 'highs': [], 'lows': [], 'closes': [], 'volumes': [], 'colors': []
    }
    out_range_data = {
        'dates': [], 'opens': [], 'highs': [], 'lows': [], 'closes': [], 'volumes': [], 'colors': []
    }

    sorted_dates = sorted(time_series.keys())
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    for date_str in sorted_dates:
        current_date = datetime.strptime(date_str, '%Y-%m-%d')
        values = time_series[date_str]
        
        # Parse values
        open_price = float(values['1. open'])
        high_price = float(values['2. high'])
        low_price = float(values['3. low'])
        close_price = float(values['4. close'])
        volume = float(values['5. volume'])
        
        # Determine if the date is within the highlighted range
        is_in_range = True
        if start_date and end_date:
            is_in_range = start_date <= current_date <= end_date
        
        # Store data in appropriate dictionary
        target_dict = in_range_data if is_in_range else out_range_data
        
        target_dict['dates'].append(current_date)
        target_dict['opens'].append(open_price)
        target_dict['highs'].append(high_price)
        target_dict['lows'].append(low_price)
        target_dict['closes'].append(close_price)
        target_dict['volumes'].append(volume)
        target_dict['colors'].append('#26A69A' if close_price >= open_price else '#EF5350')

    return in_range_data, out_range_data

def calculate_price_change(in_range_data):
    if not in_range_data['dates']:
        return 0, 0
    
    start_price = in_range_data['opens'][0]
    end_price = in_range_data['closes'][-1]
    price_change = end_price - start_price
    price_change_percentage = (price_change / start_price) * 100
    return price_change, price_change_percentage

def create_advanced_chart(timeframe='DAILY', start_date=None, end_date=None):
    data = fetch_crypto_data(timeframe)
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3]
    )

    in_range_data, out_range_data = process_data(
        data, timeframe.capitalize(), start_date, end_date
    )

    # Add out-of-range candlesticks (gray)
    if out_range_data['dates']:
        fig.add_trace(
            go.Candlestick(
                x=out_range_data['dates'],
                open=out_range_data['opens'],
                high=out_range_data['highs'],
                low=out_range_data['lows'],
                close=out_range_data['closes'],
                name='Out of Range',
                increasing_line_color='rgba(128, 128, 128, 0.5)',
                decreasing_line_color='rgba(128, 128, 128, 0.5)',
                increasing_fillcolor='rgba(128, 128, 128, 0.5)',
                decreasing_fillcolor='rgba(128, 128, 128, 0.5)'
            ),
            row=1, col=1
        )

    # Add in-range candlesticks (colored)
    if in_range_data['dates']:
        fig.add_trace(
            go.Candlestick(
                x=in_range_data['dates'],
                open=in_range_data['opens'],
                high=in_range_data['highs'],
                low=in_range_data['lows'],
                close=in_range_data['closes'],
                name='Selected Period',
                increasing_line_color='#26A69A',
                decreasing_line_color='#EF5350',
                increasing_fillcolor='#26A69A',
                decreasing_fillcolor='#EF5350'
            ),
            row=1, col=1
        )

    # Add out-of-range volume bars (gray)
    if out_range_data['dates']:
        fig.add_trace(
            go.Bar(
                x=out_range_data['dates'],
                y=out_range_data['volumes'],
                name='Volume (Out of Range)',
                marker_color='rgba(128, 128, 128, 0.5)',
                opacity=0.5
            ),
            row=2, col=1
        )

    # Add in-range volume bars (colored)
    if in_range_data['dates']:
        fig.add_trace(
            go.Bar(
                x=in_range_data['dates'],
                y=in_range_data['volumes'],
                name='Volume',
                marker_color=in_range_data['colors'],
                opacity=0.5
            ),
            row=2, col=1
        )

    # Calculate price change for the selected period
    price_change, price_change_pct = calculate_price_change(in_range_data)

    # Add summary box
    summary_text = (
        f'Selected Period Summary:<br>'
        f'Price Change: €{price_change:,.2f}<br>'
        f'Percentage Change: {price_change_pct:.2f}%'
    )

    fig.add_annotation(
        xref='paper',
        yref='paper',
        x=0.02,
        y=0.98,
        text=summary_text,
        showarrow=False,
        font=dict(color='#cfcfcf', size=12),
        bgcolor='rgba(30,30,30,0.8)',
        bordercolor='#666666',
        borderwidth=1,
        borderpad=10,
        align='left'
    )

    # Update layout
    fig.update_layout(
        title={
            'text': 'Bitcoin/EUR Price',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title='Price (EUR)',
        yaxis2_title='Volume',
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font=dict(color='#cfcfcf'),
        dragmode='pan',
        hovermode='x unified',
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        modebar=dict(
            bgcolor='rgba(30,30,30,0.9)',
            color='#cfcfcf',
            activecolor='#ffffff'
        )
    )

    # Update axes
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.2)',
        tickfont=dict(color='#a9a9a9'),
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
            ]),
            bgcolor='#1e1e1e',
            activecolor='#666666',
            font=dict(color='#cfcfcf')
        )
    )

    for row in [1, 2]:
        fig.update_yaxes(
            gridcolor='rgba(128,128,128,0.2)',
            tickfont=dict(color='#a9a9a9'),
            row=row, col=1,
            zerolinecolor='rgba(128,128,128,0.2)'
        )

    return fig

# Example usage:
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY') # <-- Put your API key here
def get_date_from_llm(query):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "Return only the start and end dates in YYYY-MM-DD format, separated by a comma if there are two dates."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.1
            }
        )
        
        result = response.json()
        if 'error' in result:
            return f"Error: {result['error']}"
            
        date = result['choices'][0]['message']['content'].strip()
        return date

    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
query= "gime a random 2 month time period between november 26 2023 and november 9 2024 it can be wherever not necesarily starting at november 2023, just return two lines start_date: YYYY-MM-DD, end_date: YYYY-MM-DD, it has to be just that text as i jave to copy it in a code, i do not need more info than that"
date = get_date_from_llm(query)
print(date)

# Regular expression to extract the start and end dates
date_pattern = r"start_date: (\d{4}-\d{2}-\d{2}), end_date: (\d{4}-\d{2}-\d{2})"

# Use re.search to find the matches
match = re.search(date_pattern, date)

if match:
    # Extract the date strings
    start_date_str = match.group(1)
    end_date_str = match.group(2)
    
    # Convert to datetime objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
fig = create_advanced_chart(start_date=start_date, end_date=end_date)
fig.show(config={
    'scrollZoom': True,
    'displayModeBar': True,
    'modeBarButtonsToAdd': ['drawopenpath', 'eraseshape'],
    'modeBarButtonsToRemove': [],
    'displaylogo': False,
    'doubleClick': 'reset',
    'showTips': True,
})


