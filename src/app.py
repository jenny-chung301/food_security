import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from data import load_data, get_globals, get_years, get_aff_years, STAPLE_COMMODITIES
from callback import register_callbacks
from styles import *


# Load data
wfp, fao, fao_grouped, aff_index, commodity_country_set = load_data()
all_countries, min_year, max_year = get_globals(wfp)

default_country = all_countries[0]
default_year = get_years(wfp, default_country)[0]

aff_years = get_aff_years(aff_index) # list of years in descending order; doesn't match wfp years

# ================================= APP =================================

app = dash.Dash(
    __name__, title='Global Food Security', external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.FONT_AWESOME]
)
server = app.server

app.layout = dbc.Container([
    # Header section
    html.Div([
        # Top gradient bar
        html.Div(className="top-accent-bar", style=top_accent_bar_style),
        
        # Main header content
        html.Div([
            # Logo and title
            html.Div([
                html.Div([
                    html.I(className="fas fa-leaf", style=logo_icon_style)
                ], style=header_logo_container_style),
                html.Div([
                    html.H1("Global Food Security", style=header_title_style),
                    html.Span("DASHBOARD", style=header_subtitle_style)
                ], style={
                    "display": "flex",
                    "flexDirection": "column"
                })
            ], style=header_logo_container_style),
                        
            # Right-aligned controls
            html.Div([
                html.Div([
                    html.Span("Last updated: ", style=header_date_label_style),
                    html.Span("March 16, 2025", style=header_date_value_style)
                ], style=header_date_container_style),
            ], style=header_controls_style)
        ], style=header_content_style)
    ], style=header_container_style),

    # tabs
    dbc.Row([
        dbc.Tabs([
            # ================ GLOBAL TAB ================
            dbc.Tab(label="Global", tab_id="global", children=[
                # description
               html.P("Explore how commodity prices change around the world, and how that relates to undernourishment and food affordability for different countries for macroscopic insights.", 
                        style=tab_description_style, className="description-container"),
                
                # affordability row
                dbc.Row([
                    # histogram
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                html.H4("Global Distribution of Affordability Ratios"),
                                html.P("Affordability ratio is the percentage of annual income budgeted for food divided by annual food expenses.")
                            ], width=9),
                            dbc.Col([
                                dcc.Dropdown(
                                    id="year-dropdown", value=max(aff_years), clearable=False,
                                    options=[{"label": year, "value": year} for year in aff_years]
                                )
                            ], width=2)
                        ], style={"height": "15%"}),

                        dbc.Row(
                            dcc.Graph(id="aff-hist", config={"responsive": True}, style={"height": "100%"}),
                            style={"height": "80%"}
                        )
                    ], width=8, style={"margin": "1rem 0 0", "height": "100%"}),

                    # summary statistics
                    dbc.Col([
                        html.Div([
                            dbc.Row(html.H5("Total Countries Included")),
                            dbc.Row([
                                dbc.Col(html.H1(id="total-countries"))
                            ], style=stat_card_row_style)
                        ], style=stat_card_container_style),

                        html.Div([
                            dbc.Row([
                                html.Div([
                                    html.H5("Average Affordability Index", style={"display": "inline-block", "margin-right": "5px"}),
                                    html.Sup("?", id="avg-change-info", style=tooltip_style),
                                    dbc.Tooltip(
                                        "Average food affordability in developing countries—higher values indicate better affordability.",
                                        target="avg-change-info",
                                        placement="top"
                                    )
                                ], style={"display": "flex", "align-items": "center"})
                            ]),
                            dbc.Row([
                                dbc.Col(html.H1(id="avg-aff-index")), 
                                dbc.Col(html.H5(id="avg-change-text"))
                            ], style=stat_card_row_style)
                        ], style=stat_card_container_style),

                        html.Div([
                            dbc.Row(html.H5("Countries Under Average Affordability")),
                            dbc.Row([
                                dbc.Col(html.H1(id="pct-countries-under-avg")),
                                dbc.Col(html.H5(id="pct-change-text"))
                            ], style=stat_card_row_style)
                        ], style=stat_card_container_style)
                        
                    ], width=4, style={
                        "height": "100%",
                        "display": "flex",               
                        "flex-direction": "column",     
                        "gap": "2rem",
                        "padding": "1rem"   
                    })

                ], style={
                    "height": "80vh",
                    "align-items": "stretch",
                    "border": "1px solid #ccc",
                    "border-radius": "5px",
                    "padding": "1rem",
                    "margin": "1rem 0",
                }),

                # filters
                dbc.Row([
                    dbc.Col([
                        html.Label("Select Countries:", className="fw-bold"),
                        dcc.Dropdown(
                            id="country-dropdown", multi=True, clearable=False,
                            options=[{"label": c, "value": c} for c in all_countries],
                            value=["Afghanistan", "Armenia", "Bangladesh", "Guinea"]
                        )
                    ], width=3),

                    dbc.Col([
                        html.Label("Select Commodity:", className="fw-bold"),
                        dcc.Dropdown(
                            id="commodity-dropdown", value="All Commodities",
                            options=[{"label": "All Commodities", "value": "All Commodities"}, {"label": "Staple Commodities", "value": "Staple Commodities"}]
                        )
                    ], width=3),

                    dbc.Col([
                        html.Label("Select Year Range:", className="fw-bold"),
                        dcc.RangeSlider(
                            id="year-slider", min=min_year, max=max_year, value=[min_year, max_year],
                            marks={year: str(year) for year in range(min_year, max_year + 1)},
                            step=1
                        )
                    ], width=6)
                ]),

                # change in global commodity prices and undernourishment
                dbc.Row([
                    dbc.Col([
                        html.H4("Global Changes in Food Commodity Prices"),
                        html.P([
                            "Staple commodities are the most widely consumed food items",
                            html.Br(),
                            "across countries, such as sugar, flour, and eggs."
                        ], style={"color": "#777"}),
                        dcc.Graph(id="price-chart", config={"responsive": True}, style=double_graph_style)
                    ], style=graph_container_style),

                    dbc.Col([
                        html.H4("Percentage of Population that is Undernourished"),
                        html.P("Data covers the last 10 years, with the most recent from 2021", style={"color": "#777"}),
                        dcc.Graph(id="line-chart", config={"responsive": True}, style=double_graph_style)
                    ], style=graph_container_style)

                ], style={ # row style
                    "height": "70vh",
                    "align-items": "stretch",
                    "gap": "2.5rem",
                    "padding": "1rem 0",
                    "margin": "1rem 0"
                })
            ]),

            # ================ COUNTRY TAB ================
            dbc.Tab(label="Country", tab_id="country", children=[
                # description
                html.P(["Explore variability of food prices across regions within a specific country for microscopic insights.",
                        html.Br(),
                        html.Em("Click a region on the map below to filter the box plot and bar plot.")
                        ], style=tab_description_style, className="description-container"),

                # filters
                dbc.Row([
                    dbc.Col([
                        html.Label("Select Country", className="fw-bold"),
                        dcc.Dropdown(
                            id="country", value=default_country, clearable=False,
                            options=[{"label": i, "value": i} for i in all_countries],
                        )
                    ], width=3),

                    dbc.Col([
                        html.Label("Select Year", className="fw-bold"),
                        dcc.Dropdown(
                            id="year", value=default_year, clearable=False, className="mb-3",
                            options=[{"label": i, "value": i} for i in get_years(wfp, default_country)]
                        )
                    ], width=2)
                ]),
                dbc.Row([
                    # ------------ MAP ------------
                    dbc.Col([
                        html.Div([
                            html.H5("Food Price Volatility Across Regions"),
                            html.Div(
                                dcc.Graph(
                                    id="map-graph",
                                    config={"responsive": True},
                                    style={"height": "100%", "width": "100%"}
                                ), style=map_style
                            )
                        ])
                    ], width=5, style={"padding": "1rem"}), 

                    # ------------ Boxplot & Barplot ------------
                    dbc.Col([
                        html.Div([
                            dcc.Store(id="average-store", data=aff_index.to_dict("records")),
                            html.Div(
                                id="country-info", 
                                className="mt-4 w-100 fade-in"
                            ) 
                        ], className="dashboard-panel"),
                        html.Div([
                            html.H5("Price Distribution for Category of Commodity"),
                            dcc.Graph(id="boxplot-frame", config={"responsive": True}, style=bar_box_style)
                        ], style=graph_container_style),
                        html.Br(),

                        html.Div([
                            html.H5("Top 20 Commodities by Average Price"),
                            dcc.Graph(id="bar-frame", config={"responsive": True}, style=bar_box_style)
                        ], style=graph_container_style)
                    ], width=6)
                ])
            ])
        ], id="tabs", active_tab="global", style=tabs_style)
    ], justify="start", style={"padding": "0px 50px"})
], fluid=True) # style={"backgroundColor": "#F6F8FA"}

register_callbacks(app, wfp, aff_index, fao_grouped, STAPLE_COMMODITIES)

# run server
if __name__ == "__main__":
    app.run_server(debug=False, dev_tools_hot_reload=False)
    # app.run_server(debug=True)
