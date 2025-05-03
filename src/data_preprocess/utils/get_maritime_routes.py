

import pandas as pd
import itertools
from geopy.geocoders import Nominatim
import requests

# Load the file





def has_osm_port(city_name):
    geolocator = Nominatim(user_agent="port-checker")
    location = geolocator.geocode(city_name)
    if not location:
        return False

    lat, lon = location.latitude, location.longitude

    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["harbour"](around:50000,{lat},{lon});
      way["harbour"](around:50000,{lat},{lon});
      relation["harbour"](around:50000,{lat},{lon});
    );
    out body;
    """
    response = requests.post(overpass_url, data={"data": query})
    data = response.json()
    return len(data.get("elements", [])) > 0



# Filter cities with ports

def get_routes_from_city(df, city:pd.Series):
    """
    Generate routes between the old cities and the new one.
    :param df: DataFrame containing city names and coordinates
    :param city: row
    :return: DataFrame with route information
    """
    ports_df = df[df['has_port'] == True, df['name'] != city['name']]
    if ports_df.empty:
        return pd.DataFrame()
    routes = []

    for index, row in ports_df.iterrows():
        route = {
            "route_name": f"{row['name']}-{city['name']}",
            "olon": row['lon'],
            "olat": row['lat'],
            "dlon": city['lon'],
            "dlat": city['lat']
        }
        routes.append(route)
    for index, row in ports_df.iterrows():
        route = {
            "route_name": f"{city['name']}-{row['name']}",
            "olon": city['lon'],
            "olat": city['lat'],
            "dlon": row['lon'],
            "dlat": row['lat']
        }
        routes.append(route)
    return pd.DataFrame(routes)

def get_routes(df):
    """
    Generate routes between cities with ports.
    :param df: DataFrame containing city names and coordinates
    :return: DataFrame with route information
    """
    routes = []
    for index, row in df.iterrows():
        routes_df = get_routes_from_city(df, row)
        if not routes_df.empty:
            routes.append(routes_df)
    return pd.concat(routes, ignore_index=True) if routes else pd.DataFrame()
    

if __name__ == "__main__":
    # Load your CSV
    df = pd.read_csv("data/cities.csv")
    df['has_port'] = df['name'].apply(has_osm_port)
    df.to_csv("data/cities.csv", index=False)

    df = df[df['has_port'] == True]

    # Get routes
    routes_df = get_routes(df)

    # Save result (optional)
    routes_df.to_csv("data/port_routes.csv", index=False)
