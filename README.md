# FleetFlow Application

## Overview
FleetFlow is a desktop application designed for efficient fleet and logistics management. It provides modules for vehicle registry, trip dispatching, maintenance logging, driver registry, fuel logging, and comprehensive analytics and reports. The application is built using Python with the Tkinter library for the graphical user interface.

## Features
-   **Vehicle Registry:** Manage your fleet vehicles, track their status (active/out of service), and view key details.
-   **Driver Registry:** Keep a record of your drivers, their license expiry, safety scores, and duty status.
-   **Trip Dispatcher:** Create, dispatch, complete, and cancel trips, assigning vehicles and drivers.
-   **Maintenance & Service Logs:** Log and track maintenance activities for your vehicles.
-   **Fuel Logging:** Record fuel consumption and costs for each vehicle.
-   **Dashboard:** Get a quick overview of key performance indicators (KPIs) for your fleet operations.
-   **Operational Analytics & Financial Reports:** Generate detailed reports on operational costs, fuel efficiency, vehicle ROI, and more, with filtering options.
-   **Role-Based Access Control:** Permissions are managed based on user roles (Manager, Dispatcher, Safety, Finance).

## Installation

### Prerequisites
-   Python 3.x (3.8 or newer recommended)

### Steps

1.  **Clone the repository(or download and unzip it):**
    ```bash
    git clone <repository_url>
    cd fleetflow-app
    ```
    (Note: Replace `<repository_url>` with the actual URL of your GitHub repository once it's created.)

2.  **Create and activate a virtual environment(optional):**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```



## How to Run

After setting up the virtual environment and installing dependencies:

### On Linux/macOS:
1.  Make sure you are in the project's root directory.
2.  Run the application using the python executable inside the virtual environment:
    ```bash
    .venv/bin/python -m fleetflow.app
    ```

### On Windows:
1.  Make sure you are in the project's root directory.
2.  Run the application using the python executable inside the virtual environment:
    ```cmd
    .venv\Scripts\python -m fleetflow.app
    ```
    if you don't want to use a virtual environment then simply run:
   ```cmd
    .venv\Scripts\python -m fleetflow.app
    ```


## Usage

### Login
-   The application starts with a login screen.
-   You can log in with different roles to test access control:
    -   **Email:** `manager@fleetflow.com`, **Password:** `admin123`, **Role:** `Manager`
    -   **Email:** `dispatcher@fleetflow.com`, **Password:** `dispatch123`, **Role:** `Dispatcher`
    -   **Email:** `safety@fleetflow.com`, **Password:** `safety123`, **Role:** `Safety`
    -   **Email:** `finance@fleetflow.com`, **Password:** `finance123`, **Role:** `Finance`
-   (Note: These are example credentials; a real application would have a proper user management system.)

### Navigation
-   After logging in, you will be directed to the Main Menu.
-   From the Main Menu, you can access various modules by clicking on their respective buttons.
-   Each module typically has a "Back to Main Menu" button to return.

## Contributing
Feel free to fork the repository, make improvements, and submit pull requests.


