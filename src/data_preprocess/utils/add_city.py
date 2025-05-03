import pandas as pd
from src.data_preprocess.utils.get_lat_long import get_coordinates
from src.data_preprocess.utils.get_maritime_routes import get_routes_from_city as get_maritime_routes
from src.data_preprocess.utils.get_roads import get_routes as get_road_routes
from src.data_preprocess.utils.get_lat_long import has_osm_port




def add_city(city_df, routes_df, city_name):
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
        "has_airport": False,
        "has_port": False
    })
    print(new_city)
    # check if the city already exists
    if city_name in city_df['name'].values:
        print(f"City {city_name} already exists in the DataFrame.")
        return city_df, routes_df
    city_df = pd.concat([city_df, new_city.to_frame().T], ignore_index=True)


    # Generate routes for the new city
    new_maritime_routes_df = get_maritime_routes(city_df, new_city)
    



    return city_df, routes_df


if __name__ == "__main__":
    # Example usage
    city_df = pd.read_csv("data/cities.csv")
    routes_df = pd.read_csv("data/routes.csv")
    city_name = "New City"
    city_df, routes_df = add_city(city_df, routes_df, city_name)
    print(city_df[city_df['name'] == city_name])