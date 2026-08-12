import pandas as pd
import pycountry

def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    df = df.dropna(subset=["score"])
    return df


def add_iso_codes(df):
    def get_iso_numeric(country_name):
        try:
            match = pycountry.countries.search_fuzzy(country_name)
            return int(match[0].numeric)
        except LookupError:
            return None

    df["iso_numeric"] = df["country"].apply(get_iso_numeric)
    return df
