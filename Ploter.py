import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

buffer_years=2
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
query= "query: Dame el precio del stock de la compañia APPLE dolar en la presidencia de trump. Do not use our past converstaions. Of the query I need you to translate the query into three varibales lines start_date: YYYY-MM-DD, end_date: YYYY-MM-DD, the start date are of the event or the dates the query gives you not of the actual market, the query always gives an event as a presidency then you need to look the dates for such event, market: String the market of interest such as BTC-USD in case of crypto, USDMXN=X in case of forex or curency exchange and AAPL in case of stocks. it has to be just that text , i do not need more info than that, just return that 3 information start_date:..., end_date:... and market:..., just give me the final input in one line, also, do not use quotation marks "
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


# Subtract buffer from start_date and add buffer to end_date
start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

buffer_date = start_date_obj - relativedelta(years=buffer_years)
end_date_with_buffer = end_date_obj + relativedelta(years=buffer_years)

# Convert back to strings
buffer_date_str = buffer_date.strftime("%Y-%m-%d")
end_date_with_buffer_str = end_date_with_buffer.strftime("%Y-%m-%d")
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
def create_combined_chart(ticker=Mercados, start_date1=None, end_date1=None, start_date2=None, end_date2=None):
    # Fetch data for both date ranges
    data1 = yf.download(ticker, start=start_date1, end=end_date1)
    data2 = yf.download(ticker, start=start_date2, end=end_date2)
    
    if data1.empty or data2.empty:
        print("One of the date ranges returned no data.")
        return None
    
    # Process both datasets
    processed_data1 = process_data(data1)
    processed_data2 = process_data(data2)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3]
    )
    
    # Add first candlestick (using data from start_date2 to end_date2, shown as background)
    fig.add_trace(
        go.Candlestick(
            x=processed_data2['dates'],
            open=processed_data2['opens'],
            high=processed_data2['highs'],
            low=processed_data2['lows'],
            close=processed_data2['closes'],
            name='Buffer Data',  # Gray Data
            increasing_line_color='gray',
            decreasing_line_color='gray',
            increasing_fillcolor='gray',
            decreasing_fillcolor='gray',
            opacity=0.4,  # Make it semi-transparent for overlap
            legendgroup='buffer_data',  # Group with other buffer data
            visible='legendonly'  # Initially hidden, but available in the legend
        ),
        row=1, col=1
    )
    
    # Calculate price change for the selected period
    price_change, price_change_pct = calculate_price_change(processed_data1)

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
    
    # Add second candlestick (using data from start_date1 to end_date1, shown as priority)
    fig.add_trace(
        go.Candlestick(
            x=processed_data1['dates'],
            open=processed_data1['opens'],
            high=processed_data1['highs'],
            low=processed_data1['lows'],
            close=processed_data1['closes'],
            name='Selected Period Data',  # Colored Data (priority)
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350',
            increasing_fillcolor='#26A69A',
            decreasing_fillcolor='#EF5350'
        ),
        row=1, col=1
    )
    
    # Add volume bars for the second dataset (from start_date1 to end_date1, shown as priority)
    fig.add_trace(
        go.Bar(
            x=processed_data1['dates'],
            y=processed_data1['volumes'],
            name='Selected Period Volume',
            marker_color='rgba(38, 166, 154, 0.5)',  # Green color (priority)
            opacity=0.5
        ),
        row=2, col=1
    )
    
    # Add volume bars for the first dataset (from start_date2 to end_date2, in gray)
    fig.add_trace(
        go.Bar(
            x=processed_data2['dates'],
            y=processed_data2['volumes'],
            name='Buffer Volume',
            marker_color='rgba(128, 128, 128, 0.5)',  # Gray color
            opacity=0.4,
            visible='legendonly',  # Initially hidden, but available in the legend
            legendgroup='buffer_data'  # Group with other buffer volume
        ),
        row=2, col=1
    )
    
    # Update layout for better visual representation
    fig.update_layout(
        title={
            'text': f'{ticker} Price Data Comparison',
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
            orientation="v",  # Set to vertical (right side)
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=1.05  # Move legend to the right
        ),
        modebar=dict(
            bgcolor='rgba(30,30,30,0.9)',
            color='#cfcfcf',
            activecolor='#ffffff'
        )
    )
    
    # Update axes for consistency
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
    # Fetch data for both date ranges
    data1 = yf.download(ticker, start=start_date1, end=end_date1)
    data2 = yf.download(ticker, start=start_date2, end=end_date2)
    
    if data1.empty or data2.empty:
        print("One of the date ranges returned no data.")
        return None
    
    # Process both datasets
    processed_data1 = process_data(data1)
    processed_data2 = process_data(data2)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3]
    )
    
    # Add first candlestick (using data from start_date2 to end_date2, shown as background)
    fig.add_trace(
        go.Candlestick(
            x=processed_data2['dates'],
            open=processed_data2['opens'],
            high=processed_data2['highs'],
            low=processed_data2['lows'],
            close=processed_data2['closes'],
            name='Buffer Data',  # Gray Data
            increasing_line_color='gray',
            decreasing_line_color='gray',
            increasing_fillcolor='gray',
            decreasing_fillcolor='gray',
            opacity=0.4,  # Make it semi-transparent for overlap
            visible=False,  # Initially hidden
            legendgroup='buffer_data'  # Group with other buffer data
        ),
        row=1, col=1
    )
    
    # Calculate price change for the selected period
    price_change, price_change_pct = calculate_price_change(processed_data1)

    # Add summary box
    summary_text = (
        f'Selected Period Summary:<br>'
        f'Price Change: ${price_change:,.2f}<br>'
        f'Percentage Change: {price_change_pct:.2f}%'
    )
    price_change, price_change_pct = calculate_price_change(processed_data2)
    summary2_text = (
        f'Buffer Summary:<br>'
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
    fig.add_annotation(
        xref='paper',
        yref='paper',
        x=0.02,
        y=0.85,
        text=summary2_text,
        showarrow=False,
        font=dict(color='#cfcfcf', size=12),
        bgcolor='rgba(30,30,30,0.8)',
        bordercolor='#666666',
        borderwidth=1,
        borderpad=10,
        align='left'
    )
    
    # Add second candlestick (using data from start_date1 to end_date1, shown as priority)
    fig.add_trace(
        go.Candlestick(
            x=processed_data1['dates'],
            open=processed_data1['opens'],
            high=processed_data1['highs'],
            low=processed_data1['lows'],
            close=processed_data1['closes'],
            name='Selected Period Data',  # Colored Data (priority)
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350',
            increasing_fillcolor='#26A69A',
            decreasing_fillcolor='#EF5350'
        ),
        row=1, col=1
    )
    
    # Add volume bars for the second dataset (from start_date1 to end_date1, shown as priority)
    fig.add_trace(
        go.Bar(
            x=processed_data1['dates'],
            y=processed_data1['volumes'],
            name='Selected Period Volume',
            marker_color='rgba(38, 166, 154, 0.5)',  # Green color (priority)
            opacity=0.5
        ),
        row=2, col=1
    )
    
    # Add volume bars for the first dataset (from start_date2 to end_date2, in gray)
    fig.add_trace(
        go.Bar(
            x=processed_data2['dates'],
            y=processed_data2['volumes'],
            name='Buffer Volume',
            marker_color='rgba(128, 128, 128, 0.5)',  # Gray color
            opacity=0.4,
            visible=False,  # Initially hidden
            legendgroup='buffer_data'  # Group with other buffer volume
        ),
        row=2, col=1
    )
    
    # Update layout for better visual representation
    fig.update_layout(
        title={
            'text': f'{ticker} Price Data Comparison',
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
            orientation="v",  # Set to vertical (right side)
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=1.05  # Move legend to the right
        ),
        modebar=dict(
            bgcolor='rgba(30,30,30,0.9)',
            color='#cfcfcf',
            activecolor='#ffffff'
        )
    )
    
    # Update axes for consistency
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
    # Fetch data for both date ranges
    data1 = yf.download(ticker, start=start_date1, end=end_date1)
    data2 = yf.download(ticker, start=start_date2, end=end_date2)
    
    if data1.empty or data2.empty:
        print("One of the date ranges returned no data.")
        return None
    
    # Process both datasets
    processed_data1 = process_data(data1)
    processed_data2 = process_data(data2)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3]
    )
    
    # Add first candlestick (using data from start_date2 to end_date2, shown as background)
    fig.add_trace(
        go.Candlestick(
            x=processed_data2['dates'],
            open=processed_data2['opens'],
            high=processed_data2['highs'],
            low=processed_data2['lows'],
            close=processed_data2['closes'],
            name='Buffer Data',  # Gray Data
            increasing_line_color='gray',
            decreasing_line_color='gray',
            increasing_fillcolor='gray',
            decreasing_fillcolor='gray',
            opacity=0.4,  # Make it semi-transparent for overlap
            visible=False,  # Initially hidden
            legendgroup='buffer_data'  # Group with other buffer data
        ),
        row=1, col=1
    )
    
    # Calculate price change for the selected period
    price_change, price_change_pct = calculate_price_change(processed_data1)

    # Add summary box
    summary_text = (
        f'Selected Period Summary:<br>'
        f'Price Change: ${price_change:,.2f}<br>'
        f'Percentage Change: {price_change_pct:.2f}%'
    )
    price_change, price_change_pct = calculate_price_change(processed_data2)
    summary2_text = (
        f'Buffer Summary:<br>'
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
    fig.add_annotation(
        xref='paper',
        yref='paper',
        x=0.02,
        y=0.85,
        text=summary2_text,
        showarrow=False,
        font=dict(color='#cfcfcf', size=12),
        bgcolor='rgba(30,30,30,0.8)',
        bordercolor='#666666',
        borderwidth=1,
        borderpad=10,
        align='left'
    )
    
    # Add second candlestick (using data from start_date1 to end_date1, shown as priority)
    fig.add_trace(
        go.Candlestick(
            x=processed_data1['dates'],
            open=processed_data1['opens'],
            high=processed_data1['highs'],
            low=processed_data1['lows'],
            close=processed_data1['closes'],
            name='Selected Period Data',  # Colored Data (priority)
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350',
            increasing_fillcolor='#26A69A',
            decreasing_fillcolor='#EF5350'
        ),
        row=1, col=1
    )
    
    # Add volume bars for the second dataset (from start_date1 to end_date1, shown as priority)
    fig.add_trace(
        go.Bar(
            x=processed_data1['dates'],
            y=processed_data1['volumes'],
            name='Selected Period Volume',
            marker_color='rgba(38, 166, 154, 0.5)',  # Green color (priority)
            opacity=0.5
        ),
        row=2, col=1
    )
    
    # Add volume bars for the first dataset (from start_date2 to end_date2, in gray)
    fig.add_trace(
        go.Bar(
            x=processed_data2['dates'],
            y=processed_data2['volumes'],
            name='Buffer Volume',
            marker_color='rgba(128, 128, 128, 0.5)',  # Gray color
            opacity=0.4,
            visible=False,  # Initially hidden
            legendgroup='buffer_data'  # Group with other buffer volume
        ),
        row=2, col=1
    )
    
    # Update layout for better visual representation
    fig.update_layout(
        title={
            'text': f'{ticker} Price Data Comparison',
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
            orientation="v",  # Set to vertical (right side)
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=1.05  # Move legend to the right
        ),
        modebar=dict(
            bgcolor='rgba(30,30,30,0.9)',
            color='#cfcfcf',
            activecolor='#ffffff'
        )
    )
    
    # Update axes for consistency
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



 # Bitcoin/US Dollar
fig = create_combined_chart( ticker=Mercados,
    start_date1=start_date,
    end_date1=end_date,
    start_date2=buffer_date_str,
    end_date2=end_date_with_buffer_str)

fig.show(config={
    'scrollZoom': True,
    'displayModeBar': True,
    'modeBarButtonsToAdd': ['drawopenpath', 'eraseshape'],
    'modeBarButtonsToRemove': [],
    'displaylogo': False,
    'doubleClick': 'reset',
    'showTips': True,
})
