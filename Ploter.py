import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import re

load_dotenv()
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
query= "query: Dame el precio de pesos por dolar en la presidencia de trump. Do not use our past converstaions. Of the query I need you to translate the query into three varibales lines start_date: YYYY-MM-DD, end_date: YYYY-MM-DD, market: String the market of interest such as BTC-USD in case of crypto, USDMXN=X in case of forex or curency exchange and APPL in case of stocks. it has to be just that text , i do not need more info than that, just return that 3 information start_date:..., end_date:... and market:..., just give me the final input in one line, also, do not use quotation marks "
date = get_date_from_llm(query)
print(date)

pattern = r"start_date:\s*(\d{4}-\d{2}-\d{2}),\s*end_date:\s*(\d{4}-\d{2}-\d{2}),\s*market:\s*([A-Z0-9\-=/]+)"
match = re.search(pattern, date)


if match:
    start_date = match.group(1)
    end_date = match.group(2)
    market = match.group(3)
else:
    print("No dates found.")

Mercados = market
def fetch_crypto_data(ticker=Mercados, start_date=None, end_date=None):
    # Use Yahoo Finance to fetch cryptocurrency data
    data = yf.download(ticker, start=start_date, end=end_date)
    return data
    
def process_data(data):
    
    # Access the 'Open', 'High', 'Low', 'Adj Close', and 'Volume' columns properly using the MultiIndex
    opens = data['Open', Mercados].tolist()  # Access 'Open' column under 'Price' level
    highs = data['High', Mercados].tolist()  # Access 'High' column
    lows = data['Low', Mercados].tolist()  # Access 'Low' column
    closes = data['Adj Close', Mercados].tolist()  # Access 'Adj Close' column
    volumes = data['Volume', Mercados].tolist()  # Access 'Volume' column
    
    # You can proceed to handle your data here, including separating in-range and out-of-range dates
    return {
        'dates': data.index.tolist(),  # Ensure the Date is used as the x-axis
        'opens': opens,
        'highs': highs,
        'lows': lows,
        'closes': closes,
        'volumes': volumes
    }

def calculate_price_change(data):
    # Calculate the price change over the selected period
    if len(data['dates']) == 0:
        return 0, 0
    
    start_price = data['opens'][0]
    end_price = data['closes'][-1]
    price_change = end_price - start_price
    price_change_percentage = (price_change / start_price) * 100
    return price_change, price_change_percentage

def create_advanced_chart(ticker=Mercados, start_date=None, end_date=None):
    # Fetch the data from Yahoo Finance
    data = fetch_crypto_data(ticker, start_date, end_date)
    
    # Process the data for plotting
    processed_data = process_data(data)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3]
    )

    # Add candlestick plot
    fig.add_trace(
        go.Candlestick(
            x=processed_data['dates'],
            open=processed_data['opens'],
            high=processed_data['highs'],
            low=processed_data['lows'],
            close=processed_data['closes'],
            name='Price Data',
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350',
            increasing_fillcolor='#26A69A',
            decreasing_fillcolor='#EF5350'
        ),
        row=1, col=1
    )

    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=processed_data['dates'],
            y=processed_data['volumes'],
            name='Volume',
            marker_color='rgba(128, 128, 128, 0.5)',
            opacity=0.5
        ),
        row=2, col=1
    )

    # Calculate price change for the selected period
    price_change, price_change_pct = calculate_price_change(processed_data)

    # Add summary box
    summary_text = (
        f'Selected Period Summary:<br>'
        f'Price Change: ${price_change:,.2f}<br>'
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
            'text': f'{ticker} Price Data',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title='Price (USD)',
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
# Example usage:


 # Bitcoin/US Dollar
fig = create_advanced_chart(ticker=Mercados, start_date=start_date, end_date=end_date)
fig.show(config={
    'scrollZoom': True,
    'displayModeBar': True,
    'modeBarButtonsToAdd': ['drawopenpath', 'eraseshape'],
    'modeBarButtonsToRemove': [],
    'displaylogo': False,
    'doubleClick': 'reset',
    'showTips': True,
})
