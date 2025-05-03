import pandas as pd
from src.data_preprocess.utils.get_lat_long import get_coordinates
from src.data_preprocess.utils.get_maritime_routes import get_routes_from_city as get_maritime_routes
from src.data_preprocess.utils.get_roads import get_rp_routes, get_boat_time_proxy

from src.data_preprocess.utils.get_maritime_routes import run_searoute, has_osm_port
from src.data_preprocess.utils.json_to_maritime import process_out_to_roads
from src.data_preprocess.utils.add_CO2_price import add_co2_and_price_df




def add_city(city_df, routes_df, city_name, 
             has_airport=False,
             intermediate_mari_path="data/port_routes-temp.csv",
             geojson_path="data/out-temp.geojson",
             ):
    """
    Add a new city to the DataFrame with default values.
    :param df: DataFrame containing city names and coordinates
    :param city_name: Name of the new city to add
    :return: DataFrame with the new city added
    """
    lat, long = get_coordinates(city_name)
    new_city = pd.Series({
        "name": city_name,
        "lat": lat,
        "lon": long,
        "has_airport": has_airport,
        "has_port": False
    })
    print(new_city)
    # check if the city already exists
    if city_name in city_df['name'].values:
        print(f"City {city_name} already exists in the DataFrame.")
        return city_df, routes_df
    city_df = pd.concat([city_df, new_city.to_frame().T], ignore_index=True)
    # city_df.to_csv(new_cities_path, index=False)


    # Generate routes for the new city
    if has_osm_port(city_name):
        new_maritime_routes_df = get_maritime_routes(city_df, new_city)
        new_maritime_routes_df.to_csv(intermediate_mari_path, index=False)
        run_searoute(intermediate_mari_path, geojson_path)
        ship_routes_df = process_out_to_roads(
            port_routes_path=intermediate_mari_path,
            geojson_path=geojson_path
        )
        ship_routes_df["time"] = ship_routes_df.apply(lambda x: get_boat_time_proxy((x["distance"])))
    else:
        ship_routes_df = pd.DataFrame(columns=["route_name", "olat", "olon", "dlat", "dlon"])
        

    plane_routes_df = get_rp_routes(city_df, new_city, type="airplane")
    road_routes_df = get_rp_routes(city_df, new_city, type="road")

    global_routes_df = pd.concat([
        plane_routes_df,
        road_routes_df,
        ship_routes_df
    ], ignore_index=True)
    global_routes_df = global_routes_df[["type", "route_name", "origin", "destination",
                                          "time", "distance", "olat", "olon", "dlat", "dlon"]]
    global_routes_df = add_co2_and_price_df(global_routes_df)

    return city_df, global_routes_df


if __name__ == "__main__":
    # Example usage
    city_df = pd.read_csv("data/cities.csv")
    routes_df = pd.read_csv("data/routes.csv")
    city_name = "Stanford"
    city_df, routes_df = add_city(city_df, routes_df, city_name,intermediate_mari_path="data/port_routes2.csv", geojson_path="data/out2.geojson")
    print(city_df[city_df['name'] == city_name])