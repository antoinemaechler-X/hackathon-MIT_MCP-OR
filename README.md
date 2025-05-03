# hackaton_MIT

## Project Overview

This project provides an interactive interface to generate the optimal freight transport route between two cities, according to the importance given to time, cost, and environmental impact (CO₂ emissions). Users can select their origin and destination, adjust their preferences for speed, price, and sustainability, and instantly receive the best route using a multi-modal network (road, air, ship). The backend processes real-world data and computes the best solution based on your priorities.

---

## Getting Started

1. Navigate to the project directory:
    ```bash
    cd hackaton_MIT
    ```

2. Install `uv` : 
(on macOS, use Homebrew):
```bash
brew install uv
```

(on Linux, use apt or yum depending on your distribution):
```bash
# For Debian/Ubuntu-based systems
sudo apt update && sudo apt install uv

# For Red Hat/CentOS-based systems
sudo yum install uv
```

(on Windows, use Chocolatey):
```bash
choco install uv
```

3. Create the .venv
    ```bash
    uv sync
    ```

4. To add a dependency, use:
    ```bash
    uv add <dependency-name>
    ```

5. To remove a dependency, use:
    ```bash
    uv remove <dependency-name>
        ```

6. To run a Python file, use:
    ```bash
    uv run python <file-name>.py
    ```
    or  activate the virtual environment, with:
        ```bash
        source .venv/bin/activate
        ```
    (on Windows, use `. .venv\Scripts\Activate.ps1`)                 
    Once activated, you can run your Python file directly:
        ```bash
        python <file-name>.py
        ```


## Running the app
launching the backend server:
```bash
    uvicorn main:app --reload
```
Then in a new terminal, run the frontend:
```bash
    npm start
```
Note : This requires Node.js and npm to be installed. If you don't have them, you can download them from [Node.js official website](https://nodejs.org/).


## Project Structure
### Backend
The first part of the project was gathering data and creating a database of cities and routes.
Initially, we picked 30 US cities and used open source APIs to gather data on their geographical coordinates, airports, and ports. We then generated a list of all possible routes between these cities, including road, air, and ship routes. The data was enriched with estimated travel times, distances, CO2 emissions, and prices.
This grid allows us to cover the US territory but should the user input a city that is not in the list, the program will add it to the database and generate the routes for it.


### Solver
The second part was translating the problem into a linear programming problem. We used gurobipy to create a model that minimizes the cost of transportation while respecting the constraints of time and CO2 emissions. The model takes into account the user's preferences for speed, price, and sustainability.
The solver uses the data from the database to find the optimal route between the two selected cities.

### Frontend
Then we developped a tool to visualize the results. The user can select the origin and destination cities, adjust the importance of time, cost, and CO2 emissions, and see the best route on a map. 

## MCP
We added Claude for real-time change detection and to provide the user with the best route at any time. The user can input traffic information, weather conditions, and other factors that may affect the route. The program will then recalculate the best route based on these inputs.