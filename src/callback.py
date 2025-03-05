from dash.dependencies import Input, Output

from data import get_years
from plots import (
    get_map,
    get_box_plot,
    get_bar_plot,
    get_price_chart,
    get_undernourishment_chart,
)


def register_callbacks(app, wfp, fao_grouped, essential_commodities):
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

                df_chk = wfp[
                    (wfp["country"] == country) & (wfp["date"].dt.year == year)
                ]
                if region_candidate in df_chk["admin2"].unique():
                    region = region_candidate

        return get_box_plot(wfp, country, year, region)

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

                df_chk = wfp[
                    (wfp["country"] == country) & (wfp["date"].dt.year == year)
                ]
                if region_candidate in df_chk["admin2"].unique():
                    region = region_candidate

        return get_bar_plot(wfp, country, year, region)
