import pandas as pd

# Read the routes dataset
routes_df = pd.read_csv('data/routes.csv')

# Calculate the means
mean_time = routes_df['time'].mean()
mean_co2 = routes_df['CO2'].mean()
mean_price = routes_df['price'].mean()

print(f"Mean travel time across all routes: {mean_time:.2f} hours")
print(f"Mean CO2 emissions across all routes: {mean_co2:.2f} kg")
print(f"Mean price across all routes: ${mean_price:.2f}")

# Calculate means by transport mode
print("\nMeans by transport mode:")
for mode in routes_df['type'].unique():
    mode_data = routes_df[routes_df['type'] == mode]
    print(f"\n{mode.capitalize()}:")
    print(f"  Mean time: {mode_data['time'].mean():.2f} hours")
    print(f"  Mean CO2: {mode_data['CO2'].mean():.2f} kg")
    print(f"  Mean price: ${mode_data['price'].mean():.2f}") 