import pandas as pd

def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    df = df.dropna(subset=["score"])
    return df