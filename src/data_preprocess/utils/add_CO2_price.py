import pandas as pd

def add_CO2_and_price(df,type='plane' co2_per_km=0.1, price_per_km=0.05):
    """
    Add CO2 and price columns to the DataFrame based on distance and type
    :param df: DataFrame containing distance and type columns
    :param type: Type of transport (e.g., 'plane', 'ship', 'road')
    :param co2_per_km: CO2 emissions per km for the specified type
    :param price_per_km: Price per km for the specified type
    """
    

    