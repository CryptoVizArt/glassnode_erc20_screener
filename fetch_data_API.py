import requests
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Constants
API_KEY = '2lZRFGaqFiEYkzr7WUuT4EaoC1X'
SINCE_DATE = int(datetime(2023, 1, 1).timestamp())
UNTIL_DATE = int(datetime.now().timestamp())

# URLs for fetching data
METRICS = [
    'https://api.glassnode.com/v1/metrics/market/price_usd_close',
    'https://api.glassnode.com/v1/metrics/market/mvrv'
]

# List of all assets (split into chunks for readability)
ASSETS = [
    'BTC', 'ETH', 'LTC', '1INCH', 'AAVE', 'ABT', 'ACH', 'ACX'
]

def fetch_glassnode_data(url, asset='BTC'):
    """
    Fetches data from Glassnode API for a specific metric and asset.
    """
    params = {
        'a': asset,
        's': SINCE_DATE,
        'u': UNTIL_DATE,
        'api_key': API_KEY,
        'f': 'CSV',
        'c': 'USD'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        metric_name = url.split('/')[-1]
        column_name = f"{metric_name}_{asset}"
        df.columns = ['t', column_name]
        df['t'] = pd.to_datetime(df['t'], unit='s')
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {asset} from {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error processing data for {asset} from {url}: {e}")
        return None

def fetch_all_data():
    """
    Fetches data for all metrics and assets and combines them into a single DataFrame.
    """
    all_dfs = []
    for metric_url in METRICS:
        for asset in ASSETS:
            print(f"Fetching {metric_url.split('/')[-1]} for {asset}")
            df = fetch_glassnode_data(metric_url, asset)
            if df is not None:
                all_dfs.append(df)

    if not all_dfs:
        raise Exception("No data was successfully fetched")

    merged_df = all_dfs[0]
    for df in all_dfs[1:]:
        merged_df = pd.merge(merged_df, df, on='t', how='outer')

    merged_df.set_index('t', inplace=True)
    return merged_df

try:
    final_df = fetch_all_data()
    print("Data collection complete")
    print(f"DataFrame shape: {final_df.shape}")
    print("\nColumns in the dataset:")
    print(final_df.columns.tolist())
except Exception as e:
    print(f"Error in data collection process: {e}")

print(final_df.tail())