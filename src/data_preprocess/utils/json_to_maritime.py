####
# This script takes a GeoJSON file with maritime routes and a CSV file with road routes,
# and enriches the CSV file with additional information from the GeoJSON file.
###

import pandas as pd
import json

def process_out_to_roads(port_routes_path, geojson_path):
    SHIP_SPEED_KMH = 30
    routes_df = pd.read_csv(port_routes_path)
    with open(geojson_path, "r") as f:
        geojson = json.load(f)
    geo_routes = {feature["properties"]["route_name"]: {
            "distance": float(feature["properties"].get("distKM", 0)),
            "type": "ship",
            "time": None,
            "origin": feature["properties"]["route_name"].split("-")[0],
            "destination": feature["properties"]["route_name"].split("-")[1],
            "CO2": None,
            "price": None,
        }
        for feature in geojson["features"]
    }
    def enrich_row(row):
        route_props = geo_routes.get(row["route_name"])
        if route_props:
            return pd.Series({
                "type": route_props["type"],
                "origin": route_props["origin"],
                "destination": route_props["destination"],
                "distance": float(route_props["distance"]),
                "CO2": route_props["CO2"],
                "price": route_props["price"],
                "time": float(route_props["distance"])/SHIP_SPEED_KMH,
            })
        else:
            return pd.Series({
                "type": None,
                "origin": None,
                "destination": None,
                "distance": None,
                "CO2": None,
                "price": None,
                "time": None,
            })
    routes_df[["type", "origin", "destination", "distance", "CO2", "price", "time"]] = routes_df.apply(enrich_row, axis=1)
    routes_df = routes_df[["type", "route_name", "origin", "destination","time", "distance", "CO2", "price", "olon", "olat", "dlon", "dlat"]]
    return routes_df
