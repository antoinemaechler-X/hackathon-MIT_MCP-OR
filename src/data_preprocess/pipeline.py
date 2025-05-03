import pandas as pd
from src.data_preprocess.utils.get_lat_long import apply_lat_long
from src.data_preprocess.utils.get_maritime_routes import has_osm_port, get_routes
from src.data_preprocess.utils import add_CO2_price
from src.data_preprocess.utils.json_to_maritime import process_out_to_roads
from src.data_preprocess.utils.get_roads import generate_all_routes
from src.data_preprocess.utils.add_CO2_price import add_co2_and_price_df
import subprocess
import os
from src.data_preprocess.utils.get_maritime_routes import has_osm_port

# 1. Ajout des coordonnées aux villes
def enrich_cities_with_coordinates(cities_path):
    df = pd.read_csv(cities_path)
    df = apply_lat_long(df)
    df.to_csv(cities_path, index=False)
    print(df.head())
    df.to_csv(cities_path, index=False)
    return df



# 2. Ajout colonne has_port et génération des routes maritimes potentielles
def generate_maritime_routes(cities_path, port_routes_path):
    df = pd.read_csv(cities_path)
    if 'has_port' not in df.columns:
        df['has_port'] = df['name'].apply(has_osm_port)
        df.to_csv(cities_path, index=False)
    ports_df = df[df['has_port'] == True]
    routes_df = get_routes(ports_df)
    routes_df.to_csv(port_routes_path, index=False)
    return routes_df

# 3. Calcul des distances maritimes avec searoute (appel Java)
def run_searoute(port_routes_path, out_geojson_path):
    searoute_dir = os.path.join('src', 'data_preprocess', 'searoute')
    searoute_jar = os.path.join(searoute_dir, 'searoute.jar')
    cmd = [
        'java', '-jar', 'searoute.jar',
        '-i', os.path.relpath(os.path.abspath(port_routes_path), searoute_dir),
        '-o', os.path.relpath(os.path.abspath(out_geojson_path), searoute_dir)
    ]
    subprocess.run(cmd, check=True, cwd=searoute_dir)

# 4. Traitement des routes maritimes avec out_to_roads
def process_maritime_routes():
    routes_df = process_out_to_roads(
        port_routes_path='data/port_routes.csv',
        geojson_path='data/out.geojson'
    )
    routes_df.to_csv('data/ship_routes.csv', index=False)

# 5. Génération des routes avion et route
def generate_airplane_and_road_routes():
    generate_all_routes('data/cities.csv')

# 6. Ajout du prix et CO2 et concaténation
def add_price_and_co2_and_concat():
    for type in ["airplane", "road", "ship"]:
        df = pd.read_csv(f"data/{type}_routes.csv")
        df["type"] = type
        df.to_csv(f"data/{type}_routes.csv", index=False)
    # combine
    global_df = pd.concat([
        pd.read_csv("data/airplane_routes.csv"),
        pd.read_csv("data/road_routes.csv"),
        pd.read_csv("data/ship_routes.csv")
    ], ignore_index=True)
    global_df = add_co2_and_price_df(global_df)
    global_df.to_csv("data/routes.csv", index=False)
    
if __name__ == "__main__":
    cities_path = 'data/cities.csv'
    port_routes_path = 'data/port_routes.csv'
    out_geojson_path = 'data/out.geojson'

    cities_df = enrich_cities_with_coordinates(cities_path)
    routes_df = generate_maritime_routes(cities_path, port_routes_path)
    run_searoute(port_routes_path, out_geojson_path)
    process_maritime_routes()
    generate_airplane_and_road_routes()
    add_price_and_co2_and_concat()
    print("Pipeline terminée. Les routes sont dans data/routes.csv")
