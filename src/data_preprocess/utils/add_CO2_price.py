import pandas as pd

PLANE_CO2_PER_KM = 1.019 # kg CO2 per km for plane
SHIP_CO2_PER_KM = 0.005  # kg CO2 per km for ship
ROAD_CO2_PER_KM = 0.120  # kg CO2 per km for road
TRAIN_CO2_PER_KM = 0.0278  # kg CO2 per km for train

PLANE_PRICE_PER_KM = 0.10  # price per km for plane
SHIP_PRICE_PER_KM = 0.02  # price per km for ship
ROAD_PRICE_PER_KM = 0.05  # price per km for road


def add_CO2_price_row(row):
    if row["type"] == "airplane":
        row["CO2"] = row["distance"] * PLANE_CO2_PER_KM
        row["price"] = row["distance"] * PLANE_PRICE_PER_KM
    elif row["type"] == "ship":
        row["CO2"] = row["distance"] * SHIP_CO2_PER_KM
        row["price"] = row["distance"] * SHIP_PRICE_PER_KM
    elif row["type"] == "road":
        row["CO2"] = row["distance"] * ROAD_CO2_PER_KM
        row["price"] = row["distance"] * ROAD_PRICE_PER_KM
    elif row["type"] == "train":
        row["CO2"] = row["distance"] * TRAIN_CO2_PER_KM
        row["price"] = row["distance"] * ROAD_PRICE_PER_KM
    return row

def add_co2_and_price_df(df):
    df = df.copy()
    df["CO2"] = None
    df["price"] = None
    df = df.apply(add_CO2_price_row, axis=1)
    return df




if __name__ == "__main__":
    # for type in ["airplane", "road", "ship","train"]:
    #     df = pd.read_csv(f"data/{type}_routes.csv")
    #     df["type"] = type
    #     df.to_csv(f"data/{type}_routes.csv", index=False)
    # # combine
    # global_df = pd.concat([
    #     pd.read_csv("data/airplane_routes.csv"),
    #     pd.read_csv("data/road_routes.csv"),
    #     pd.read_csv("data/ship_routes.csv")
    # ], ignore_index=True)
    # global_df = global_df[["type", "route_name", "origin", "destination", "time", "distance", "CO2", "price", "olon", "olat", "dlon", "dlat"]]

    # global_df.to_csv("data/routes.csv", index=False)
    routes = pd.read_csv("data/train_routes2.csv")
    routes = add_co2_and_price_df(routes)
    routes = routes[["type", "route_name", "origin", "destination", "time", "distance", "CO2", "price", "olon", "olat", "dlon", "dlat"]]
    routes.to_csv("data/train_routes2.csv", index=False)
