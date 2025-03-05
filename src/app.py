import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from data import load_data, get_globals, get_years, ESSENTIAL_COMMODITIES
from callback import register_callbacks


# Load data
wfp, fao, fao_grouped, commodity_country_set = load_data()
all_countries, min_year, max_year = get_globals(wfp)

default_country = all_countries[0]
default_year = get_years(wfp, default_country)[0]


# ================================= APP =================================

app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.FONT_AWESOME]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Tabs(
                        [
                            # ================ GLOBAL TAB ================
                            dbc.Tab(
                                label="Global",
                                tab_id="global",
                                children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Select Countries:",
                                                        className="fw-bold",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="country-dropdown",
                                                        options=[
                                                            {"label": c, "value": c}
                                                            for c in all_countries
                                                        ],
                                                        value=[
                                                            "Russia",
                                                            "China",
                                                            "Vietnam",
                                                            "Thailand",
                                                        ],
                                                        multi=True,
                                                        clearable=False,
                                                    ),
                                                    html.Br(),
                                                    html.Label(
                                                        "Select Commodity:",
                                                        className="fw-bold",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="commodity-dropdown",
                                                        options=[
                                                            {
                                                                "label": "All Commodities",
                                                                "value": "All Commodities",
                                                            },
                                                            {
                                                                "label": "Essential Commodities",
                                                                "value": "Essential Commodities",
                                                            },
                                                        ],
                                                        value="All Commodities",
                                                    ),
                                                    html.Br(),
                                                    html.Label(
                                                        "Select Year Range:",
                                                        className="fw-bold",
                                                    ),
                                                    dcc.RangeSlider(
                                                        id="year-slider",
                                                        min=min_year,
                                                        max=max_year,
                                                        value=[min_year, max_year],
                                                        marks={
                                                            year: str(year)
                                                            for year in range(
                                                                min_year, max_year + 1
                                                            )
                                                        },
                                                        step=1,
                                                    ),
                                                ],
                                                width=4,
                                                className="d-flex flex-column",
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        [
                                                            html.H4(
                                                                "Global Changes in Foold Commodity Prices"
                                                            ),
                                                            html.P(
                                                                "Essential Commodities include Sugar, Wheat flour, Eggs, "
                                                                "Potatoes, Salt, Fuel, Tomatoes, Rice, Oil, and Onions",
                                                                style={"color": "#777"},
                                                            ),
                                                            dcc.Graph(id="price-chart"),
                                                        ],
                                                        style={
                                                            "border": "1px solid #ccc",
                                                            "padding": "1rem",
                                                            "margin": "1rem 0",
                                                        },
                                                    ),
                                                    html.Br(),
                                                    html.Div(
                                                        [
                                                            html.H4(
                                                                "Percentage of Population That Is Undernourished"
                                                            ),
                                                            html.P(
                                                                "Data Covers the Last 10 Years, with the Most Recent from 2021",
                                                                style={"color": "#777"},
                                                            ),
                                                            dcc.Graph(id="line-chart"),
                                                        ],
                                                        style={
                                                            "border": "1px solid #ccc",
                                                            "padding": "1rem",
                                                            "margin": "1rem 0",
                                                        },
                                                    ),
                                                ],
                                                width="auto",
                                                className="d-flex flex-column",
                                            ),
                                        ]
                                    )
                                ],
                            ),
                            # ================ COUNTRY TAB ================
                            dbc.Tab(
                                label="Country",
                                tab_id="country",
                                children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Select Country",
                                                        className="fw-bold",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="country",
                                                        value=default_country,
                                                        options=[
                                                            {"label": i, "value": i}
                                                            for i in all_countries
                                                        ],
                                                        clearable=False,
                                                    ),
                                                ],
                                                width=3,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Select Year",
                                                        className="fw-bold",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="year",
                                                        value=default_year,
                                                        options=[
                                                            {"label": i, "value": i}
                                                            for i in get_years(
                                                                wfp, default_country
                                                            )
                                                        ],
                                                        clearable=False,
                                                        className="mb-3",
                                                    ),
                                                ],
                                                width=2,
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    dbc.Row(
                                        [  # ------------ MAP ------------
                                            dbc.Col(
                                                html.Div(
                                                    [
                                                        html.H5(
                                                            "Food Price Volatility Across Regions"
                                                        ),
                                                        html.Div(
                                                            dcc.Graph(
                                                                id="map-graph",
                                                                config={
                                                                    "responsive": True
                                                                },
                                                                style={
                                                                    "height": "100%",
                                                                    "width": "100%",
                                                                },
                                                            ),
                                                            style={
                                                                "border": "1px solid #ccc",
                                                                "border-radius": "5px",
                                                                "padding": "0",
                                                                "overflow": "hidden",
                                                                "backgroundColor": "white",
                                                                "height": "600px",
                                                                "width": "100%",
                                                            },
                                                        ),
                                                    ],
                                                    style={"padding": "1rem"},
                                                ),
                                                width=5,
                                            ),
                                            # ------------ Boxplot & Barplot ------------
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        [
                                                            html.H5(
                                                                "Price Distribution for Category of Commodity"
                                                            ),
                                                            html.Iframe(
                                                                id="boxplot-frame",
                                                                style={
                                                                    "border": "0",
                                                                    "width": "100%",
                                                                    "height": "300px",
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                    html.Br(),
                                                    html.Div(
                                                        [
                                                            html.H5(
                                                                "Top 20 Commodities"
                                                            ),
                                                            html.Iframe(
                                                                id="bar-frame",
                                                                style={
                                                                    "border": "0",
                                                                    "width": "100%",
                                                                    "height": "310px",
                                                                    "overflow": "hidden",
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                width=7,
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                        id="tabs",
                        active_tab="global",
                        style={
                            "width": "250px",
                            "line-height": "8px",
                            "align-items": "center",
                            "margin-left": "0",
                            "margin-top": "30px",
                            "margin-bottom": "30px",
                        },
                    ),
                    width=12,
                    style={"padding": "0px 50px"},
                )
            ],
            justify="start",
        )
    ],
    fluid=True,
)

register_callbacks(app, wfp, fao_grouped, ESSENTIAL_COMMODITIES)

# run server
if __name__ == "__main__":
    app.run_server(debug=True)
