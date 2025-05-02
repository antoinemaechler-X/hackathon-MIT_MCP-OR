####
# This script takes a GeoJSON file with maritime routes and a CSV file with road routes,
# and enriches the CSV file with additional information from the GeoJSON file.
###


import pandas as pd
import json

# Load your routes file
routes_df = pd.read_csv("data/port_routes.csv")  # Must have route_name, olon, olat, dlon, dlat

# Load the GeoJSON file
with open("data/out.geojson", "r") as f:
    geojson = json.load(f)

# Build a dictionary from geojson route_name → properties
geo_routes = {feature["properties"]["route_name"]: {
        "distance": float(feature["properties"].get("distKM", 0)),
        "type": "ship",  # static
        "time": None,    # optional: estimate later
        "origin": feature["properties"]["route_name"].split("-")[0],
        "destination": feature["properties"]["route_name"].split("-")[1],
        "CO2": None,
        "price": None,
    }
    for feature in geojson["features"]
}

# Add distance, time, type, origin, destination to your routes_df
def enrich_row(row):
    route_props = geo_routes.get(row["route_name"])
    if route_props:
        return pd.Series({
            "type": route_props["type"],
            "origin": route_props["origin"],
            "destination": route_props["destination"],
            "distance": route_props["distance"],
            "time": route_props["time"],
            "CO2": route_props["CO2"],
            "price": route_props["price"],
        })
    else:
        return pd.Series({
            "type": None,
            "origin": None,
            "destination": None,
            "distance": None,
            "time": None,
            "CO2": None,
            "price": None,
        })

routes_df[["type", "origin", "destination", "distance", "time", "CO2", "price"]] = routes_df.apply(enrich_row, axis=1)

# sort the columns
routes_df = routes_df[["type", "route_name", "origin", "destination","time", "distance", "CO2", "price", "olon", "olat", "dlon", "dlat"]]

# Save to new file
routes_df.to_csv("data/routes_with_maritime_info.csv", index=False)
