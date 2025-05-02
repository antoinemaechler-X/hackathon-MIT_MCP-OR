## This script adds latitude and longitude to a CSV file with city names.


import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep
import sys


# Function to get coordinates
def get_coordinates(city):
    try:
        location = geolocator.geocode(city)
        if location:
            return pd.Series([location.latitude, location.longitude])
    except:
        return pd.Series([None, None])
    return pd.Series([None, None])


if __name__ == "__main__":
    # Example usage
    # df = pd.DataFrame({'city': ['Paris', 'New York', 'Tokyo']})
    # df[['lat', 'lon']] = df['city'].apply(get_coordinates)
    # print(df)
    if len(sys.argv) < 3:
        path = "data/cities.csv"
    else:
        path = sys.args[1]

    if len(sys.argv) < 4:
        new_path = path
    else:
        new_path = sys.argv[2]
# Load your CSV
    df = pd.read_csv(path)

    # Set up geolocato
    geolocator = Nominatim(user_agent="city-geocoder")

    # Apply to each row with a pause to avoid rate limiting
    df[['lat', 'lon']] = df['name'].apply(lambda x: get_coordinates(x) if pd.notna(x) else pd.Series([None, None]))
        # Add pause between requests
    sleep(1)

    # Save result
    df.to_csv(new_path, index=False)
