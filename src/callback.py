import dash
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash import dcc, html

from .data import get_years
from .plots import (
    get_map,
    get_box_plot,
    get_bar_plot,
    get_price_chart,
    get_undernourishment_chart,
    get_hist,
)


def register_callbacks(app, wfp, aff_index, fao_grouped, essential_commodities):
    # callback to update undernourishment chart
    @app.callback(
        Output("price-chart", "figure"),
        [
            Input("country-dropdown", "value"),
            Input("year-slider", "value"),
            Input("commodity-dropdown", "value"),
        ],
    )
    def update_price_chart(selected_countries, year_range, selected_commodity):
        return get_price_chart(
            wfp,
            selected_countries,
            year_range,
            selected_commodity,
            essential_commodities,
        )

    # Callbacks to update dropdown and map graph dynamically
    @app.callback(
        [Output("year", "options"), Output("year", "value")], Input("country", "value")
    )
    def update_year_options(selected_country):
        available_years = get_years(wfp, selected_country)
        return [{"label": i, "value": i} for i in available_years], available_years[0]

    # callback to update the undernourishment chart
    @app.callback(
        Output("line-chart", "figure"),
        [Input("country-dropdown", "value"), Input("year-slider", "value")],
    )
    def update_undernourishment_chart(selected_countries, year_range):
        if fao_grouped is None or fao_grouped.empty or not selected_countries:
            raise PreventUpdate
        return get_undernourishment_chart(fao_grouped, selected_countries, year_range)

    # callback to update the map
    @app.callback(
        Output("map-graph", "figure"),
        [Input("country", "value"), Input("year", "value")],
    )
    def update_map(country, year):
        return get_map(wfp, country, year)

    # callback to update the boxplot
    @app.callback(
        Output("boxplot-frame", "figure"),
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

                df_chk = wfp[
                    (wfp["country"] == country) & (wfp["date"].dt.year == year)
                ]
                if region_candidate in df_chk["admin2"].unique():
                    region = region_candidate

        return get_box_plot(wfp, country, year, region)

    # callback to update the barplot
    @app.callback(
        Output("bar-frame", "figure"),
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
        - If that region doesn't exist in the new country/year, ignore it (show entire)..
        """
        region = None

        if clickData and "points" in clickData and len(clickData["points"]) > 0:

            point_data = clickData["points"][0]
            if "customdata" in point_data and point_data["customdata"]:
                region_candidate = point_data["customdata"][0]  # admin2

                df_chk = wfp[
                    (wfp["country"] == country) & (wfp["date"].dt.year == year)
                ]
                if region_candidate in df_chk["admin2"].unique():
                    region = region_candidate

        return get_bar_plot(wfp, country, year, region)

    # callback to update histogram
    @app.callback(
        Output(
            "aff-hist", "figure"
        ),  # The figure output should be directly assigned to the `figure` attribute
        [Input("year-dropdown", "value")],
    )
    def update_hist(selected_year):
        return get_hist(aff_index, selected_year)

    # callback to update summary statistics
    @app.callback(
        [
            Output("avg-aff-index", "children"),
            Output("pct-countries-under-avg", "children"),
            Output("avg-change-text", "children"),
            Output("pct-change-text", "children"),
            Output("avg-change-text", "style"),
            Output("pct-change-text", "style"),
        ],
        [Input("year-dropdown", "value")],
    )
    def update_summary_stats(selected_year):
        prev_year = selected_year - 1

        values = {}
        for year in [selected_year, prev_year]:
            if year not in aff_index["year"].values:
                continue  # skip if year is not in dataset

            values[year] = {}

            # filter data for specific year
            subset = aff_index[aff_index["year"] == year]

            avg_index = subset["affordability_index"].mean()
            total_countries = len(subset)
            num_under = len(subset[subset["affordability_index"] < avg_index])

            values[year]["mean_index"] = subset["affordability_index"].mean()
            values[year]["pct_under"] = (num_under / total_countries) * 100

        curr_avg = values[selected_year]["mean_index"]
        curr_pct_under = values[selected_year]["pct_under"]

        # format the results
        avg_aff_index_text = f"{curr_avg:.2f}"
        pct_under_avg_text = f"{curr_pct_under:.1f}%"

        # calculate percentage changes if prev year exists
        if prev_year in values:
            prev_avg = values[prev_year]["mean_index"]
            prev_pct_under = values[prev_year]["pct_under"]

            avg_change = ((curr_avg - prev_avg) / prev_avg) * 100
            pct_change = curr_pct_under - prev_pct_under

            # Format the changes with the + sign for positive changes
            avg_change_text = (
                f"+{avg_change:.2f}%" if avg_change > 0 else f"{avg_change:.2f}%"
            )
            pct_change_text = (
                f"+{pct_change:.2f}%" if pct_change > 0 else f"{pct_change:.2f}%"
            )

            # Determine color based on positive or negative change
            avg_change_style = {"color": "green" if avg_change >= 0 else "red"}
            pct_change_style = {"color": "green" if pct_change >= 0 else "red"}
        else:
            # if no prev year, leave empty
            avg_change_text = ""
            pct_change_text = ""
            avg_change_style = {}
            pct_change_style = {}

        return (
            avg_aff_index_text,
            pct_under_avg_text,
            avg_change_text,
            pct_change_text,
            avg_change_style,
            pct_change_style,
        )

    # Callback to update country-info based on selected country and year
    @app.callback(
        Output("country-info", "children"),
        [
            Input("average-store", "data"),
            Input("country", "value"),
            Input("year", "value"),
        ],
    )
    def update_country_info(average_data, country, year):
        if not average_data:
            return html.P("No data available", className="text-center text-muted fs-4")

        current_index = next(
            (
                item["affordability_index"]
                for item in average_data
                if item["country"] == country and item["year"] == year
            ),
            None,
        )

        previous_index = next(
            (
                item["affordability_index"]
                for item in average_data
                if item["country"] == country and item["year"] == year - 1
            ),
            None,
        )

        if current_index is None:
            return html.P("No data available", className="text-center text-muted fs-4")

        if previous_index is not None and previous_index != 0:
            yoy_growth = ((current_index - previous_index) / previous_index) * 100
            yoy_text = f"YoY Growth: {yoy_growth:.2f}%"
            yoy_color = (
                "text-success"
                if yoy_growth > 0
                else "text-danger" if yoy_growth < 0 else "text-muted"
            )
        else:
            yoy_text = "YoY Growth: N/A"
            yoy_color = "text-muted"

        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H5(
                        f"Affordability Index for {country}",
                        className="text-center fw-bold",
                    )
                ),
                dbc.CardBody(
                    [
                        html.P(
                            f"{current_index:.2f}",
                            className="text-center fw-bold text-primary display-3",
                        ),
                        html.P(
                            yoy_text, className=f"text-center fw-bold {yoy_color} fs-5"
                        ),
                    ],
                    className="d-flex flex-column align-items-center justify-content-center",
                    style={"height": "150px"},
                ),
            ],
            className="md-5 shadow-sm",
            style={
                "margin-bottom": "20px",
                "border": "0",
                "border-radius": "10px",
                "height": "200px",
                "width": "100%",
                "box-shadow": "3px 3px 15px rgba(0, 0, 0, 0.2)",
            },
        )
