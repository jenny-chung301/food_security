import pandas as pd
import altair as alt
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# load data
wfp = pd.read_parquet("../data/processed/wfp_preprocessed.parquet")
fao = pd.read_csv("../data/raw/FAOSTAT_data_en_nutrition.csv")
df = wfp  # Assuming wfp is the dataframe you're working with for this functionality

# ================================= FOOD PRICES =================================
# get unique countries, years, and commodities for the dropdown/slider
all_countries = sorted(wfp["country"].unique())
min_year = wfp["date"].dt.year.min()
max_year = wfp["date"].dt.year.max()
all_commodities = ["All Commodities", "Essential Commodities"]

# list of essential commodities
essential_commodities = [
    "Sugar",
    "Wheat flour",
    "Eggs",
    "Potatoes",
    "Salt",
    "Fuel (diesel)",
    "Tomatoes",
    "Rice",
    "Oil (vegetable)",
    "Onions",
]

# group by commodity to get a set of countries available for each commodity
commodity_country_set = (
    wfp.groupby("commodity")["country"]
    .agg(lambda x: set(x))
    .reset_index(name="countries")
)

# ================================= UNDERNOURISHMENT =================================
# preprocess FAO data
fao["Value"] = fao["Value"].astype(str).str.replace("<", "", regex=False).astype(float)
fao["Year"] = fao["Year"].astype(str).str[:4].astype(int)
fao_grouped = fao.groupby(["Year", "Area"], as_index=False)["Value"].mean()
fao_grouped["Value"] = fao_grouped["Value"].fillna(0)

# ================================= MAP =================================


def get_years(country):
    return sorted(df[df["country"] == country]["date"].dt.year.unique(), reverse=True)


default_country = all_countries[0]
default_year = get_years(default_country)[0]


# Helper function for generating map
def get_map(country, year, df=df):
    df_prep = df[df["country"] == country]
    df_grouped = (
        df_prep.groupby([df_prep["date"].dt.year, "admin2", "latitude", "longitude"])[
            "standardprice"
        ]
        .mean()
        .reset_index()
    )
    df_grouped["standardprice"] = df_grouped["standardprice"].apply(
        lambda x: round(x, 3)
    )
    df_grouped_year = df_grouped[df_grouped["date"] == year]

    fig = px.scatter_map(
        df_grouped_year,
        lat="latitude",
        lon="longitude",
        size="standardprice",
        color="standardprice",
        color_continuous_scale="Oranges",
        hover_name="admin2",
        hover_data={"latitude": False, "longitude": False},
        zoom=5,
        height=700,
        width=500,
        custom_data=["admin2"],
    )
    fig.update_layout(
        map_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_showscale=False,
    )
    fig.update_traces(
        hoverlabel=dict(
            bordercolor="rgba(0,0,0,0)",
            font=dict(color="black"),
        )
    )

    return fig


# ================================= Boxplot =================================
alt.data_transformers.disable_max_rows()


# drawing the box plot for categories
def get_box_plot(country, year, region=None, df=df):

    df_box = df[(df["country"] == country) & (df["date"].dt.year == year)]
    if region is not None:
        df_box = df_box[df_box["admin2"] == region]

    box = (
        alt.Chart(df_box)
        .mark_boxplot()
        .encode(
            x=alt.X(
                "category:N",
                axis=alt.Axis(labelAngle=30, labelFontSize=15, titleFontSize=20),
            ),
            y=alt.Y(
                "standardprice:Q",
                axis=alt.Axis(labelFontSize=15, titleFontSize=20),
                title="Price in USD",
            ),
            color=alt.Color("category:N"),
        )
        .properties(width=450, height=250)
    )
    return box.to_html()


# ================================= Barplot =================================
# Drawing the bar plot for top 20 commodities
def get_bar_plot(country, year, region=None, df=df):

    df_bar = df[(df["country"] == country) & (df["date"].dt.year == year)][
        ["admin2", "category", "commodity", "standardprice"]
    ]
    if region is not None:
        df_bar = df_bar[df_bar["admin2"] == region]

    df_bar = (
        df_bar.groupby(["category", "commodity"])["standardprice"]
        .mean()
        .reset_index()
        .sort_values("standardprice", ascending=False)[:20]
    )
    df_bar["standardprice"] = df_bar["standardprice"].apply(lambda x: round(x, 3))

    bar = (
        alt.Chart(df_bar)
        .mark_bar()
        .encode(
            x=alt.X(
                "commodity:N",
                axis=alt.Axis(labelAngle=30, labelFontSize=15, titleFontSize=20),
            ).sort("-y"),
            y=alt.Y(
                "standardprice:Q",
                axis=alt.Axis(labelFontSize=15, titleFontSize=20),
                title="Price in USD",
            ),
            color=alt.Color("category:N"),
            tooltip=["commodity", "standardprice"],
        )
        .properties(width=450, height=250)
    )

    return bar.to_html()


# ================================= APP =================================

# set up app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# app layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Tabs(
                            id="tabs",
                            value="global",
                            children=[
                                # ================ GLOBAL TAB ================
                                dcc.Tab(
                                    label="Global",
                                    value="global",
                                    children=[
                                        dbc.Row(
                                            [
                                                # sidebar column (4 parts wide)
                                                dbc.Col(
                                                    [
                                                        # html.H3("Filter Options", className="mb-4"),
                                                        html.Label(
                                                            "Select Countries:",
                                                            className="fw-bold",
                                                        ),
                                                        dcc.Dropdown(
                                                            id="country-dropdown",
                                                            options=[
                                                                {
                                                                    "label": country,
                                                                    "value": country,
                                                                }
                                                                for country in all_countries
                                                            ],
                                                            value=[
                                                                "Russia",
                                                                "China",
                                                                "Vietnam",
                                                                "Thailand",
                                                            ],
                                                            multi=True,
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
                                                                    "label": commodity,
                                                                    "value": commodity,
                                                                }
                                                                for commodity in all_commodities
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
                                                                    min_year,
                                                                    max_year + 1,
                                                                    1,
                                                                )
                                                            },
                                                            step=1,
                                                        ),
                                                    ],
                                                    width=4,
                                                    className="d-flex flex-column",
                                                ),
                                                # Graph column (8 parts wide)
                                                dbc.Col(
                                                    [
                                                        dbc.Card(
                                                            [
                                                                dbc.CardHeader(
                                                                    "Global Changes in Commodity Prices"
                                                                ),
                                                                dbc.CardBody(
                                                                    [
                                                                        dcc.Graph(
                                                                            id="price-chart"
                                                                        )
                                                                    ]
                                                                ),
                                                            ]
                                                        ),
                                                        html.Br(),
                                                        dbc.Card(
                                                            [
                                                                dbc.CardHeader(
                                                                    "Share of the population that is undernourished"
                                                                ),
                                                                dbc.CardBody(
                                                                    [
                                                                        dcc.Graph(
                                                                            id="line-chart"
                                                                        )
                                                                    ]
                                                                ),
                                                            ]
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
                                dcc.Tab(
                                    label="Country",
                                    value="country",
                                    children=[
                                        # Dropdowns for Country / Year
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
                                                            className="mb-3",
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
                                                                    default_country
                                                                )
                                                            ],
                                                            className="mb-3",
                                                            clearable=False,
                                                        ),
                                                    ],
                                                    width=3,
                                                ),
                                                dbc.Col([], width=6),
                                            ],
                                            className="mb-4",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [  # map card
                                                        dbc.Card(
                                                            [
                                                                dbc.CardHeader(
                                                                    "Food Price Volatility Across Regions"
                                                                ),
                                                                dbc.CardBody(
                                                                    [
                                                                        dcc.Graph(
                                                                            id="map-graph",
                                                                            figure=get_map(
                                                                                default_country,
                                                                                default_year,
                                                                            ),
                                                                            style={
                                                                                "marginLeft": "0px",
                                                                                "marginRight": "0px",
                                                                            },
                                                                        )
                                                                    ]
                                                                ),
                                                            ],
                                                            className="md-5",
                                                        )
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [  # boxplot card
                                                        dbc.Card(
                                                            [
                                                                dbc.CardHeader(
                                                                    "Price Distribution for Category of Commodity"
                                                                ),
                                                                dbc.CardBody(
                                                                    [
                                                                        html.Iframe(
                                                                            id="boxplot-frame",
                                                                            srcDoc=get_box_plot(
                                                                                default_country,
                                                                                default_year,
                                                                            ),
                                                                            style={
                                                                                "marginLeft": "0px",
                                                                                "marginRight": "0px",
                                                                                "border": "0",
                                                                                "width": "100%",
                                                                                "height": "430px",
                                                                            },
                                                                        )
                                                                    ]
                                                                ),
                                                            ],
                                                            className="md-5",
                                                        ),
                                                        html.Br(),
                                                        # barplot card
                                                        dbc.Card(
                                                            [
                                                                dbc.CardHeader(
                                                                    "Top 20 Commodities"
                                                                ),
                                                                dbc.CardBody(
                                                                    [
                                                                        html.Iframe(
                                                                            id="bar-frame",
                                                                            srcDoc=get_bar_plot(
                                                                                default_country,
                                                                                default_year,
                                                                            ),
                                                                            style={
                                                                                "marginLeft": "0px",
                                                                                "marginRight": "0px",
                                                                                "border": "0",
                                                                                "width": "100%",
                                                                                "height": "450px",
                                                                            },
                                                                        )
                                                                    ]
                                                                ),
                                                            ],
                                                            className="md-5",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ],
                            style={
                                "width": "250px",
                                "line-height": "8px",
                                "align-items": "center",
                                "margin-left": "0",
                                "margin-top": "30px",
                                "margin-bottom": "30px",
                            },
                        ),  # Styling of tab row
                    ],
                    width="full",
                    style={"padding": "0px 50px"},
                )  # Width of column that holds all content + horizontal padding
            ],
            justify="start",
        )  # Left align tabs
    ],
    fluid=True,
    # className="d-flex justify-content-center",
)


# callback to update country dropdown options dynamically based on commodity selection
@app.callback(
    Output("country-dropdown", "options"), [Input("commodity-dropdown", "value")]
)
def update_country_dropdown(selected_commodity):
    if selected_commodity == "All Commodities":
        return [{"label": country, "value": country} for country in all_countries]
    elif selected_commodity == "Essential Commodities":
        countries_for_commodity = (
            commodity_country_set[
                commodity_country_set["commodity"].isin(essential_commodities)
            ]["countries"]
            .explode()
            .unique()
        )
        return [
            {"label": country, "value": country}
            for country in sorted(countries_for_commodity)
        ]


# callback to update price chart
@app.callback(
    Output("price-chart", "figure"),
    [
        Input("country-dropdown", "value"),
        Input("year-slider", "value"),
        Input("commodity-dropdown", "value"),
    ],
)
def update_price_chart(selected_countries, year_range, selected_commodity):
    if not selected_countries:
        return {}

    start_year, end_year = year_range
    filtered_data = wfp[
        wfp["country"].isin(selected_countries)
        & wfp["date"].dt.year.between(start_year, end_year)
    ]

    if selected_commodity == "Essential Commodities":
        filtered_data = filtered_data[
            filtered_data["commodity"].isin(essential_commodities)
        ]

    result = (
        filtered_data.groupby(["country", "date"], as_index=False)["standardprice"]
        .mean()
        .rename(columns={"standardprice": "avg_usdprice"})
    )

    fig = px.line(
        result,
        x="date",
        y="avg_usdprice",
        color="country",  # title='Global Changes in Commodity Prices',
        labels={
            "avg_usdprice": "Average Price (USD)",
            "date": "Year",
            "country": "Country",
        },
        height=450,
        width=700,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )

    years = result["date"].dt.year.unique()
    max_year = result["date"].max().year
    fig.update_layout(
        # plot_bgcolor="rgba(240, 248, 255, 0.9)",
        template="simple_white",  # add
        xaxis=dict(
            title="Year",
            tickmode="array",
            tickvals=years,
            ticktext=[str(year) for year in years],
            range=[
                f"{start_year}-01-01",
                f"{max_year}-01-01",
            ],  # aligns x-axis ticks when we scale with slider
        ),
        yaxis=dict(
            title="Average Price (USD)",
            showgrid=True,  # add
            gridcolor="LightGray",  # add
            gridwidth=1,  # add
            griddash="dash",  # add)
            # hovermode="closest",
        ),
        hovermode="x unified",
    )
    fig.update_traces(
        line=dict(width=2),
        hovertemplate=("%{fullData.name}: <b>%{y}</b><extra></extra>"),  # add
    )

    return fig


# callback to update undernourishment chart
@app.callback(
    Output("line-chart", "figure"),
    [Input("country-dropdown", "value"), Input("year-slider", "value")],
)
def update_undernourishment_chart(selected_countries, year_range):
    start_year, end_year = year_range
    fao_filtered = fao_grouped[
        (fao_grouped["Area"].isin(selected_countries))
        & (fao_grouped["Year"].between(start_year, end_year))
    ]

    fig = px.line(
        fao_filtered,
        x="Year",
        y="Value",
        color="Area",
        # title="Share of the population that is undernourished",
        height=450,
        width=700,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        markers=True,  # add
    )

    years = fao_filtered["Year"].unique()
    fig.update_layout(
        # plot_bgcolor="rgba(240, 248, 255, 0.9)",
        template="simple_white",  # add
        xaxis=dict(
            title="Year",
            tickmode="array",
            tickvals=years,
            ticktext=[str(year) for year in years],
            # range=[start_year, end_year]
        ),
        yaxis=dict(
            title="Undernourishment (%)",
            showgrid=True,  # add
            gridcolor="LightGray",  # add
            gridwidth=1,  # add
            griddash="dash",  # add
        ),
        # hovermode="closest",
        hovermode="x unified",  # add
    )
    fig.update_traces(
        line=dict(width=2),
        hovertemplate=("%{fullData.name}: <b>%{y}</b><extra></extra>"),  # add
    )

    return fig


# Callbacks to update dropdown and map graph dynamically
@app.callback(
    [Output("year", "options"), Output("year", "value")], Input("country", "value")
)
def update_year_options(selected_country):
    available_years = get_years(selected_country)
    return [{"label": i, "value": i} for i in available_years], available_years[0]


# callback to update the map
@app.callback(
    Output("map-graph", "figure"), [Input("country", "value"), Input("year", "value")]
)
def update_map(country, year):
    return get_map(country, year)


# callback to update the boxplot
@app.callback(
    Output("boxplot-frame", "srcDoc"),
    [
        Input("country", "value"),
        Input("year", "value"),
        Input("map-graph", "clickData"),
    ],
)
def update_box_plot(country, year, clickData):
    """
    - If user changes country or year, show the entire box plot for that selection.
    - If user clicks on a region in the map, filter the box plot to that region.
    - If that region doesn't exist in the new country/year, ignore it (show entire).
    """
    region = None

    if clickData and "points" in clickData and len(clickData["points"]) > 0:

        point_data = clickData["points"][0]
        if "customdata" in point_data and point_data["customdata"]:
            region_candidate = point_data["customdata"][0]  # admin2

            df_chk = df[(df["country"] == country) & (df["date"].dt.year == year)]
            if region_candidate in df_chk["admin2"].unique():
                region = region_candidate

    return get_box_plot(country, year, region)


# callback to update the barplot
@app.callback(
    Output("bar-frame", "srcDoc"),
    [
        Input("country", "value"),
        Input("year", "value"),
        Input("map-graph", "clickData"),
    ],
)
def update_bar_plot(country, year, clickData):
    """
    - If user changes country or year, show the entire bar plot for that selection.
    - If user clicks on a region in the map, filter the bar plot to that region.
    - If that region doesn't exist in the new country/year, ignore it (show entire).
    """
    region = None

    if clickData and "points" in clickData and len(clickData["points"]) > 0:

        point_data = clickData["points"][0]
        if "customdata" in point_data and point_data["customdata"]:
            region_candidate = point_data["customdata"][0]  # admin2

            df_chk = df[(df["country"] == country) & (df["date"].dt.year == year)]
            if region_candidate in df_chk["admin2"].unique():
                region = region_candidate

    return get_bar_plot(country, year, region)


# run server
if __name__ == "__main__":
    app.run_server(debug=True)
