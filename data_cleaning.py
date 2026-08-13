import pandas as pd
import pycountry

def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    df = df.dropna(subset=["score"])
    return df


def add_iso_codes(df):

    country_mapping = {
        "Ivory Coast": 384,                
        "Turkey": 792,                      
        "Palestinian Territories": 275,     
        "DR Congo": 180,                  
        "Congo DR": 180,                     
    }

    def get_iso_numeric(country_name):
        if country_name in country_mapping:
            return country_mapping[country_name]

        try:
            match = pycountry.countries.search_fuzzy(country_name)
            return int(match[0].numeric)
        except LookupError:
            return None

    df["iso_numeric"] = df["country"].apply(get_iso_numeric)

    return df
