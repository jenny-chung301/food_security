import altair as alt
import plotly.express as px

# set the alt option for the large dataset
alt.data_transformers.disable_max_rows()

# For the country tab
COLOR_MAP = {
    "cereals and tubers": "rgb(102, 197, 204)",
    "miscellaneous food": "rgb(246, 207, 113)",
    "pulses and nuts": "rgb(248, 156, 116)",
    "vegetables and fruits": "rgb(220, 176, 242)",
    "oil and fats": "rgb(135, 197, 95)",
    "meat, fish and eggs": "rgb(158, 185, 243)",
    "milk and dairy": "rgb(254, 136, 177)",
}


def get_hist(aff_index, selected_year):
    filtered_data = aff_index[aff_index["year"] == selected_year]

    fig = px.histogram(
        filtered_data,
        x="affordability_ratio",
        nbins=30,  # Adjust the number of bins as needed
        # title="Distribution of Affordability Ratios (Latest Year)",
        labels={"affordability_ratio": "Affordability Ratio"},
        template="plotly_white",
    )

    fig.update_layout(
        xaxis_title="Affordability Ratio",
        yaxis_title="Number of Countries",
        bargap=0.05,
    )

    return fig


def get_price_chart(
    wfp, selected_countries, year_range, selected_commodity, essential_commodities
):
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
    result["avg_usdprice"] = result["avg_usdprice"].round(3)

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
        height=350,
        width=600,
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
            showgrid=True,
            gridcolor="LightGray",
            gridwidth=1,
            griddash="dash",
            # hovermode="closest",
        ),
        hovermode="x unified",
    )
    fig.update_traces(
        line=dict(width=2),
        hovertemplate=("%{fullData.name}: <b>%{y}</b><extra></extra>"),
    )

    return fig


def get_undernourishment_chart(fao_grouped, selected_countries, year_range):
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
        height=350,
        width=600,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        markers=True,  # add
    )

    years = fao_filtered["Year"].unique()
    fig.update_layout(
        template="simple_white",
        xaxis=dict(
            title="Year",
            tickmode="array",
            tickvals=years,
            ticktext=[str(year) for year in years],
            # range=[start_year, end_year]
        ),
        yaxis=dict(
            title="Undernourishment (%)",
            showgrid=True,
            gridcolor="LightGray",
            gridwidth=1,
            griddash="dash",
        ),
        hovermode="x unified",
    )
    fig.update_traces(
        line=dict(width=2),
        hovertemplate=("%{fullData.name}: <b>%{y}</b><extra></extra>"),
    )

    return fig


def get_map(df, country, year):
    df_prep = df[df["country"] == country]
    df_grouped = (
        df_prep.groupby([df_prep["date"].dt.year, "admin2", "latitude", "longitude"])[
            "standardprice"
        ]
        .mean()
        .reset_index()
    )
    df_grouped["standardprice"] = df_grouped["standardprice"].round(3)
    df_grouped_year = df_grouped[df_grouped["date"] == year]
    df_grouped_year["standardprice"] = df_grouped["standardprice"].fillna(0)

    fig = px.scatter_mapbox(
        df_grouped_year,
        lat="latitude",
        lon="longitude",
        size="standardprice",
        color="standardprice",
        color_continuous_scale="Oranges",
        hover_name="admin2",
        hover_data={"latitude": False, "longitude": False},
        zoom=5,
        custom_data=["admin2"],
        mapbox_style="open-street-map",  # carto-positron
    )
    fig.update_layout(
        autosize=True,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_showscale=False,
        showlegend=False,
    )
    fig.update_traces(
        hoverlabel=dict(
            bordercolor="rgba(0,0,0,0)",
            font=dict(color="black"),
        ),
    )

    return fig


def get_box_plot(df, country, year, region=None):
    df_box = df[(df["country"] == country) & (df["date"].dt.year == year)]
    if region is not None:
        df_box = df_box[df_box["admin2"] == region]

    df_box["standardprice"] = df_box["standardprice"].round(3)

    fig = px.box(
        df_box,
        x="category",
        y="standardprice",
        color="category",
        color_discrete_map=COLOR_MAP,
        labels={"category": "Food Category", "standardprice": "Average Price (USD)"},
    )

    fig.update_layout(
        template="simple_white",
        width=800,
        height=300,
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=False,
        yaxis=dict(
            title="Average Price (USD)",
            showgrid=True,
            gridcolor="LightGray",
            gridwidth=1,
            griddash="dash",
        ),
    )
    # rotate x-axis labels
    # fig.update_xaxes(tickangle=20)

    return fig


def get_bar_plot(df, country, year, region=None):
    # Filter data
    df_bar = df[(df["country"] == country) & (df["date"].dt.year == year)]
    if region is not None:
        df_bar = df_bar[df_bar["admin2"] == region]

    # Group & average
    df_bar = (
        df_bar.groupby(["category", "commodity", "Unit"])["standardprice"]
        .mean()
        .reset_index()
        .sort_values("standardprice", ascending=False)
        .head(20)
    )

    # Round prices
    df_bar["standardprice"] = df_bar["standardprice"].round(3)

    fig = px.bar(
        df_bar,
        x="commodity",
        y="standardprice",
        color="category",
        color_discrete_map=COLOR_MAP,
        labels={"standardprice": "Average Price (USD)", "commodity": "Commodity"},
        hover_data={
            "category": True,
            "commodity": True,
            "Unit": True,
        },
    )

    fig.update_xaxes(categoryorder="array", categoryarray=df_bar["commodity"].tolist())

    fig.update_layout(
        template="simple_white",
        width=800,
        height=300,
        yaxis=dict(
            title="Average Price (USD)",
            showgrid=True,
            gridcolor="LightGray",
            gridwidth=1,
            griddash="dash",
        ),
        margin=dict(l=10, r=10, t=50, b=50),
    )
    return fig
