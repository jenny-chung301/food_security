import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from data import load_data, get_globals, get_years, get_aff_years, ESSENTIAL_COMMODITIES
from plots import get_hist
from callback import register_callbacks
from styles import tabs_style, stat_card_container_style, stat_card_row_style, graph_container_style, map_style, double_graph_style, affo_country_style


# Load data
wfp, fao, fao_grouped, aff_index, commodity_country_set = load_data()
all_countries, min_year, max_year = get_globals(wfp)

default_country = all_countries[0]
default_year = get_years(wfp, default_country)[0]

aff_years = get_aff_years(aff_index) # list of years in descending order; doesn't match wfp years


# ================================= APP =================================

app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.FONT_AWESOME]
)

app.layout = dbc.Container([
    # header
    dbc.Row(),

    # tabs
    dbc.Row([
        dbc.Tabs([
            # ================ GLOBAL TAB ================
            dbc.Tab(label="Global", tab_id="global", children=[
                # affordability row
                dbc.Row([
                    # histogram
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                html.H4("Global Distribution of Affordability Ratios"),
                                html.P("Affordability ratio is calculated as (Local Price / Mean National Wage)")
                            ], width=9),
                            dbc.Col([
                                dcc.Dropdown(
                                    id="year-dropdown", value=max(aff_years), clearable=False,
                                    options=[{"label": year, "value": year} for year in aff_years]
                                )
                            ], width=2)
                        ]),
                        dbc.Row(
                            dcc.Graph(id="aff-hist")
                        )
                    ], width=8, style={"margin": "1rem 0 0"}),

                    # summary statistics
                    dbc.Col([
                        html.Div([
                            dbc.Row(html.H5("Total Countries Included")),
                            dbc.Row([
                                dbc.Col(html.H1(f"{len(all_countries)}"))
                            ], style=stat_card_row_style)
                        ], style=stat_card_container_style),
                        html.Div([
                             dbc.Row([html.Div([html.H5("Average Affordability Index",style={"display": "inline-block", "margin-right": "5px"}),
                                            html.Sup("?", id="avg-change-info", style={
                                            "color": "white",
                                            "background-color": "#777", 
                                            "cursor": "pointer",
                                            "font-size": "0.8em",
                                            "vertical-align": "super",
                                            "border-radius": "50%", 
                                            "padding": "2px 5px",
                                            "display": "inline-block",
                                            "text-align": "center",
                                            "width": "16px",  
                                            "height": "16px",
                                            "line-height": "12px",  
                                        }),
                                        dbc.Tooltip(
                                            "Average food affordability in developing countries—higher values indicate better affordability.",
                                            target="avg-change-info",
                                            placement="right"
                                        )], style={"display": "flex", "align-items": "center"}
                                        )]),
                            dbc.Row([
                                dbc.Col(html.H1(id="avg-aff-index")), 
                                dbc.Col(
                                    html.H5(id="avg-change-text", style={"color": "green"})
                                )
                            ], style=stat_card_row_style)
                        ], style=stat_card_container_style),
                        html.Div([
                            dbc.Row(html.H5("Countries Under Average Affordability")),
                            dbc.Row([
                                dbc.Col(html.H1(id="pct-countries-under-avg")),
                                dbc.Col(html.H5(id="pct-change-text", style={"color": "red"}))
                            ], style=stat_card_row_style)
                        ], style=stat_card_container_style)
                    ], width=4)

                ], style={
                    "border": "1px solid #ccc",
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
                            # value=["Russia", "China", "Vietnam", "Thailand"]
                            value=["Afghanistan", "Armenia", "Bangladesh", "Guinea"]
                        )
                    ], width=3),

                    dbc.Col([
                        html.Label("Select Commodity:", className="fw-bold"),
                        dcc.Dropdown(
                            id="commodity-dropdown", value="All Commodities",
                            options=[{"label": "All Commodities", "value": "All Commodities"}, {"label": "Essential Commodities", "value": "Essential Commodities"}]
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
                        html.P(
                            # "Essential Commodities include Sugar, Wheat flour, Eggs, "
                            "Potatoes, Salt, Fuel, Tomatoes, Rice, Oil, and Onions",
                            style={"color": "#777"}
                        ),
                        dcc.Graph(id="price-chart", config={"responsive": True}, style=double_graph_style)
                    ], width="auto", style=graph_container_style),

                    dbc.Col([
                        html.H4("Percentage of Population that is Undernourished"),
                        html.P(
                            "Data covers the last 10 years, with the most recent from 2021",
                            style={"color": "#777"}
                        ),
                        dcc.Graph(id="line-chart", config={"responsive": True}, style=double_graph_style)
                    ], width="auto", style=graph_container_style)

                ], style={
                    "display": "flex",  # Apply Flexbox layout
                    "justify-content": "space-evenly",  # Evenly space the columns
                    "align-items": "flex-start",  # Align columns at the top
                })
            ]),

            # ================ COUNTRY TAB ================
            dbc.Tab(label="Country", tab_id="country", children=[
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
                 # Add a note for users
                dbc.Row(
                    html.Div(
                        "Click a region on the map below to filter the box plot and bar plot.",
                        style={"fontStyle": "italic", "marginBottom": "1rem"}
                    )
                ),
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
                        html.Div(
                                [
                                    dcc.Store(id="average-store", data=aff_index.to_dict("records")),
                                    html.Div(
                                        id="country-info",
                                        style={"margin-top": "20px", "width": "100%"}), 

                                ],
                                    style= affo_country_style
                                ),
                        html.Div([
                            html.H5("Price Distribution for Category of Commodity"),
                            dcc.Graph(id="boxplot-frame", style={"border": "0", "width": "100%", "height": "300px"})
                        ]),
                        html.Br(),
                        html.Div([
                            html.H5("Top 20 Commodities by Average Price"),
                            dcc.Graph(id="bar-frame", style={"border": "0", "width": "100%", "height": "310px", "overflow": "hidden"})
                        ])
                    ], width=6)
                ])
            ])
        ], id="tabs", active_tab="global", style=tabs_style)
    ], justify="start", style={"padding": "0px 50px"})
], fluid=True)

register_callbacks(app, wfp, aff_index, fao_grouped, ESSENTIAL_COMMODITIES)

# run server
if __name__ == "__main__":
    # app.run_server(debug=True, dev_tools_hot_reload=False)
    app.run_server(debug=True)
