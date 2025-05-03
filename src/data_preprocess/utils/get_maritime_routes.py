

import pandas as pd
import itertools
from geopy.geocoders import Nominatim
import requests
import os
import subprocess
from src.data_preprocess.utils.json_to_maritime import process_out_to_roads

# Load the file





def has_osm_port(city_name, type="port"):
    geolocator = Nominatim(user_agent="port-checker")
    location = geolocator.geocode(city_name)
    if not location:
        return False

    lat, lon = location.latitude, location.longitude

    overpass_url = "http://overpass-api.de/api/interpreter"

    if type == "port":
        query = f"""
        [out:json];
        (
          node["port"](around:50000,{lat},{lon});
          way["port"](around:50000,{lat},{lon});
          relation["port"](around:50000,{lat},{lon});
        );
        out body;
        """
    elif type == "airport":
        query = f"""
        [out:json];
        (
          node["airport"](around:50000,{lat},{lon});
          way["aiport"](around:50000,{lat},{lon});
          relation["airport"](around:50000,{lat},{lon});
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
    if not has_osm_port(city['name']):
        return pd.DataFrame()
    ports_df = df[(df['has_port'] == True) & (df['name'] != city['name'])]
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


def run_searoute(port_routes_path, out_geojson_path):
    searoute_dir = os.path.join('src', 'data_preprocess', 'searoute')
    searoute_jar = os.path.join(searoute_dir, 'searoute.jar')
    cmd = [
        'java', '-jar', 'searoute.jar',
        '-i', os.path.relpath(os.path.abspath(port_routes_path), searoute_dir),
        '-o', os.path.relpath(os.path.abspath(out_geojson_path), searoute_dir)
    ]
    subprocess.run(cmd, check=True, cwd=searoute_dir)






if __name__ == "__main__":
    # Load your CSV
    # df = pd.read_csv("data/cities.csv")
    # df['has_port'] = df['name'].apply(has_osm_port)
    # df.to_csv("data/cities.csv", index=False)

    # df = df[df['has_port'] == True]

    # # Get routes
    # routes_df = get_routes(df)

    # # Save result (optional)
    # routes_df.to_csv("data/port_routes.csv", index=False)
    print(has_osm_port("Los Angeles", type="airport"))