import pandas as pd


# Define constants
ESSENTIAL_COMMODITIES = [
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


def load_data():

    # load data
    wfp = pd.read_parquet("../data/processed/wfp_preprocessed.parquet")
    # wfp = pd.read_parquet("../data/processed/newest_dataset.parquet")
    fao = pd.read_csv("../data/raw/FAOSTAT_data_en_nutrition.csv")
    aff_index = pd.read_csv("../data/processed/affordability_index.csv")

    # preprocess
    fao["Value"] = (
        fao["Value"].astype(str).str.replace("<", "", regex=False).astype(float)
    )
    fao["Year"] = fao["Year"].astype(str).str[:4].astype(int)

    # group
    fao_grouped = fao.groupby(["Year", "Area"], as_index=False)["Value"].mean()
    fao_grouped["Value"] = fao_grouped["Value"].fillna(0)

    commodity_country_set = (
        wfp.groupby("commodity")["country"]
        .agg(lambda x: set(x))
        .reset_index(name="countries")
    )
    return wfp, fao, fao_grouped, aff_index, commodity_country_set


def get_globals(wfp):
    all_countries = sorted(wfp["country"].unique())
    min_year = wfp["date"].dt.year.min()
    max_year = wfp["date"].dt.year.max()

    return all_countries, min_year, max_year


def get_years(df, country):
    return sorted(df[df["country"] == country]["date"].dt.year.unique(), reverse=True)
