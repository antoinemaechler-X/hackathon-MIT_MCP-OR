import pandas as pd

PLANE_CO2_PER_KM = 0.115  # kg CO2 per km for plane
SHIP_CO2_PER_KM = 0.005  # kg CO2 per km for ship
ROAD_CO2_PER_KM = 0.120  # kg CO2 per km for road

PLANE_PRICE_PER_KM = 0.10  # price per km for plane
SHIP_PRICE_PER_KM = 0.02  # price per km for ship
ROAD_PRICE_PER_KM = 0.05  # price per km for road


def add_CO2_and_price(df):
    for index, row in df.iterrows():
        if row["type"] == "airplane":
            df.at[index, "CO2"] = row["distance"] * PLANE_CO2_PER_KM
            df.at[index, "price"] = row["distance"] * PLANE_PRICE_PER_KM
        elif row["type"] == "ship":
            df.at[index, "CO2"] = row["distance"] * SHIP_CO2_PER_KM
            df.at[index, "price"] = row["distance"] * SHIP_PRICE_PER_KM
        elif row["type"] == "road":
            df.at[index, "CO2"] = row["distance"] * ROAD_CO2_PER_KM
            df.at[index, "price"] = row["distance"] * ROAD_PRICE_PER_KM
        else:
            df.at[index, "CO2"] = None
            df.at[index, "price"] = None
    return df

if __name__ == "__main__":
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
    global_df = global_df[["type", "route_name", "origin", "destination", "time", "distance", "CO2", "price", "olon", "olat", "dlon", "dlat"]]

    global_df.to_csv("data/routes.csv", index=False)
    