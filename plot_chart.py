import plotly.graph_objs as go
from plotly.subplots import make_subplots
from fetch_data import fetch_crypto_data
from process_data import process_data

def create_advanced_chart(timeframe='DAILY'):
    # Fetch data from the specified timeframe
    data = fetch_crypto_data(timeframe)
    
    # Create figure with secondary y-axis for volume
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3]
    )

    # Process data
    dates, opens, highs, lows, closes, volumes = process_data(data, timeframe.capitalize())

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

    # Add volume bars with color-coded bars
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

    # Update layout for dark mode and improved interaction
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
        dragmode='pan',  # Set default drag mode to pan
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

    # Update axes colors for dark mode
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

    # Update y-axes for both plots
    for row in [1, 2]:
        fig.update_yaxes(
            gridcolor='rgba(128,128,128,0.2)',
            tickfont=dict(color='#a9a9a9'),
            row=row, col=1,
            zerolinecolor='rgba(128,128,128,0.2)'
        )

    return fig
