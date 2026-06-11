# TFG-RaspberryPi

TFG-RaspberryPi is a project that focuses on utilizing Raspberry Pi to, during a trip in an Electric Vehicle (EV), collect data from the car and request an stop to a central server when the user feels the need to stop. The project is designed to enhance the EV driving experience by providing real-time data collection and communication capabilities.

## Project Structure
```
├── assets/               # Icons for the application
├── logs/                 # System logs
├── src/
│   ├── Domain/           # Business logic, entities, and controllers
│   ├── Persistence/      # GPS client, route client and MQTT client implementations
│   ├── Presentation/     # Layer for user interface and interaction
│   └── Utils/            # Logging and constants
├── main.py               # Application entry point
├── nmea_generator.py     # NMEA sentence generator, based on 2 points
└── pyproject.toml        # Project dependencies and configuration
```



## Setup environment

### Using `uv` (recommended)

```bash
uv sync
```

### Using `pip`

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate in Windows
pip install -e .
```

### .env

Create a `.env` file in the root directory with the following content:

```
# MQTT configuration
MQTT_BROKER_HOST =
MQTT_BROKER_PORT =

MQTT_USER =
MQTT_PASSWORD =

VEHICLE_PLATE =
MQTT_REQUESTS_TOPIC =

# Other configurations
LOG_LEVEL = "DEBUG"
```


## Program Architecture

The program follows a clean, layered architecture to separate concerns:

### 1. Presentation Layer (`src/Presentation/`)

- **emergent.py**: Contains the logic for handling emergent windows.
- **presentation.py**: Contains the logic to interact with the user, display options, and handle user input. It communicates with the domain layer to process requests and display results.
- **welcome.py**: The main entry point. Shows the options to the user and calls the presentation program with the selected option.

### 2. Domain Layer (`src/Domain/`)

Contains business logic and core entities:

- **Entities**: Models for `ChargingStation`, `Charger`, `Request`, and `Option`.
- **Controllers**:
  - `ControlPosition`: Using the GPS client, it retrieves the current position of the vehicle, or a default position if the GPS client is not available.
  - `ControlRoute`: Handles route geometry, distances, and durations using a local OSRM (Open Source Routing Machine) server.
  - `ControlRequest`: Sends the request to the central server when the user wants to stop, and handles the response.

### 3. Persistence Layer (`src/Persistence/`)

- **GPS Client**: Interacts with the GPS hardware to retrieve the current location of the vehicle. Runs in a separate thread to continuously update the position.
- **MQTT Client**: Manages the connection to the MQTT broker, subscribes to relevant topics, and handles incoming messages. It also provides methods to publish messages to the broker.
- **Route Client**: Handles external HTTP requests to the routing server.

### 4. Utils Layer (`src/Utils/`)

Contains a centralized logging configuration (`logger.py`) and global constants (`constants.py`).

## Execution

To start the client, simply run:

```bash
DISPLAY=:0 LOG_LEVEL=DEBUG uv run main.py
```

`DISPLAY=:0` is necessary to allow the application to access the display server and show the emergent windows.

`LOG_LEVEL` can be modified before `uv`: 

```bash
LOG_LEVEL=DEBUG uv run main.py
```


---

*Developed by Daniel Sánchez Castro for TFG 2026.*
