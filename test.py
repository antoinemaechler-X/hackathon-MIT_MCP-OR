import pandas as pd


df = pd.read_csv("data/airplane_routes.csv")
df["type"] = "airplane"
df.to_csv("data/airplane_routes.csv", index=False)
df = pd.read_csv("data/road_routes.csv")
df["type"] = "road"
df.to_csv("data/road_routes.csv", index=False)
