
## Data Files Overview

### `cities.csv`

This file contains the list of all cities used in the project, enriched with geographic and infrastructure information.

**Columns:**
- `name`: Name of the city.
- `lat`, `lon`: Latitude and longitude coordinates (automatically geocoded).
- `has_airport`: Boolean or integer indicating if the city has an airport.
- `has_port`: Boolean or integer indicating if the city has a port.

**How it is built:**
1. **Raw Input:** The process starts from a raw list of city names.
2. **Geocoding:** The script automatically adds latitude and longitude using the OpenStreetMap Nominatim API (`apply_lat_long` in `get_lat_long.py`).
3. **Infrastructure Detection:** The pipeline checks for the presence of airports and ports for each city using Overpass API queries (`has_osm_port` in `get_maritime_routes.py`).
4. **Result:** The output is a clean, ready-to-use table of cities with all necessary attributes for route generation.

---

### `routes_clean.csv`

This file contains all possible transportation routes between cities, including road, airplane, and ship connections.

**Columns:**
- `type`: Transport mode (`road`, `airplane`, or `ship`).
- `route_name`: Unique identifier for the route (e.g., `Paris-London`).
- `origin`, `destination`: Names of the origin and destination cities.
- `time`: Estimated travel time for the route.
- `distance`: Distance of the route (in kilometers).
- `CO2`: Estimated CO2 emissions for the route.
- `price`: Estimated price for the route.
- `olat`, `olon`: Latitude and longitude of the origin city.
- `dlat`, `dlon`: Latitude and longitude of the destination city.

**How it is built:**
1. **Route Generation:** For each pair of cities, the pipeline generates possible routes:
   - **Road and Airplane:** Calculated using haversine distance and speed proxies (`get_roads.py`).
   - **Ship:** Generated only between port cities, with distances computed using the external `searoute.jar` tool and enriched via GeoJSON (`get_maritime_routes.py` + json_to_maritime.py).
2. **Enrichment:** Each route is assigned estimated travel time, distance, CO2 emissions, and price (`add_CO2_price.py`).
3. **Concatenation:** All routes are merged into a single DataFrame and saved as `routes_clean.csv`.

---

### **Pipeline Summary**

1. **Start from raw city names.**
2. **Enrich cities with coordinates and infrastructure info.**
3. **Generate all possible routes (road, airplane, ship) between cities.**
4. **Compute distances, times, CO2, and prices for each route.**
5. **Export the results as `cities.csv` and `routes_clean.csv` for use in modeling, optimization, and visualization.**

---

**These files are the foundation for all routing, optimization, and visualization tasks in the project.**