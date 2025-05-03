import pandas as pd

# Read the routes data
routes_df = pd.read_csv('data/routes.csv')

# Calculate means
mean_time = routes_df['time'].mean()
mean_co2 = routes_df['CO2'].mean()
mean_price = routes_df['price'].mean()

print(f"Original means:")
print(f"Time: {mean_time:.2f} hours")
print(f"CO2: {mean_co2:.2f} kg")
print(f"Price: ${mean_price:.2f}")

# Normalize the values
routes_df['time'] = routes_df['time'] / mean_time
routes_df['CO2'] = routes_df['CO2'] / mean_co2
routes_df['price'] = routes_df['price'] / mean_price

# Calculate new means (should be 1.0 for all columns)
new_mean_time = routes_df['time'].mean()
new_mean_co2 = routes_df['CO2'].mean()
new_mean_price = routes_df['price'].mean()

print("\nNew means (should be 1.0):")
print(f"Time: {new_mean_time:.2f}")
print(f"CO2: {new_mean_co2:.2f}")
print(f"Price: {new_mean_price:.2f}")

# Save the normalized data
routes_df.to_csv('data/routes_normalized.csv', index=False)
print("\nNormalized data saved to 'data/routes_normalized.csv'") 