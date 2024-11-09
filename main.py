from plot_chart import create_advanced_chart

# Create and display the chart with config options for interactivity
fig = create_advanced_chart()
fig.show(config={
    'scrollZoom': True,           # Enable scroll zoom
    'displayModeBar': True,       # Always show the mode bar
    'modeBarButtonsToAdd': [      # Add additional tools
        'drawopenpath', 
        'eraseshape'
    ],
    'modeBarButtonsToRemove': [], # Keep all default buttons
    'displaylogo': False,         # Remove plotly logo
    'doubleClick': 'reset',       # Reset view on double click
    'showTips': True,             # Show tips on hover over modebar buttons
})
