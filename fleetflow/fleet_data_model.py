import uuid # Import uuid
from fleetflow.data_manager import FleetDataManager
from datetime import datetime
from enum import Enum

# -------------------------------
# Trip Status Lifecycle
# -------------------------------
class TripStatus(Enum):
    DRAFT = "Draft"
    DISPATCHED = "Dispatched"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

# -------------------------------
# Driver Status Lifecycle
# -------------------------------
class DriverStatus(Enum):
    ON_DUTY = "On Duty"
    OFF_DUTY = "Off Duty"
    SUSPENDED = "Suspended"

import inspect # Import inspect

# -------------------------------
# Base Model for entities
# -------------------------------
class BaseModel:
    def to_dict(self):
        return {k: v.value if isinstance(v, Enum) else v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data):
        # Get the signature of the __init__ method for the concrete class
        sig = inspect.signature(cls.__init__)
        init_params = sig.parameters

        # Prepare arguments for __init__, providing defaults for missing ones
        args = {}
        for name, param in init_params.items():
            if name == 'self':
                continue
            if name in data:
                # Special handling for enums
                if name == "status":
                    if cls.__name__ == "Trip":
                        args[name] = TripStatus(data[name])
                    elif cls.__name__ == "Driver":
                        args[name] = DriverStatus(data[name])
                    else:
                        args[name] = data[name] # Fallback
                else:
                    args[name] = data[name]
            elif param.default is not inspect.Parameter.empty:
                args[name] = param.default # Use default value from __init__
            else:
                # If a required parameter is missing and has no default, it's an error.
                # For now, we'll try to set a reasonable default or raise an error.
                # For numeric types, 0 or 0.0 is safe. For strings, empty string.
                # This could be more sophisticated, e.g., checking param.annotation
                if name in ["odometer", "max_capacity", "acquisition_cost", "safety_score", "cargo_weight", "liters", "cost", "start_odometer", "end_odometer"]:
                    args[name] = 0 if isinstance(param.default, int) else 0.0
                elif name in ["name", "description", "date", "license_expiry", "email", "password", "role", "vehicle_type", "region"]: # Added vehicle_type and region
                    args[name] = ""
                elif name in ["out_of_service", "available"]:
                    args[name] = False
                elif name == "status": # Default for enums
                    if cls.__name__ == "Trip": args[name] = TripStatus.DRAFT
                    elif cls.__name__ == "Driver": args[name] = DriverStatus.OFF_DUTY
                    else: args[name] = None
                elif name in ["trip_id", "log_id"]: # IDs should be generated
                    args[name] = str(uuid.uuid4()) # Generate new UUID if missing
                else:
                    # If we can't determine a safe default, raise an error or set None
                    print(f"Warning: Missing attribute '{name}' for class '{cls.__name__}' during deserialization. Setting to None.")
                    args[name] = None
        
        # Instantiate the class using the collected arguments
        return cls(**args)

# -------------------------------
# Data Models
# -------------------------------
class User(BaseModel):
    def __init__(self, email, password, role):
        self.email = email
        self.password = password
        self.role = role

class Vehicle(BaseModel):
    def __init__(self, vehicle_id, max_capacity, name="", odometer=0, out_of_service=False, acquisition_cost=0.0, vehicle_type="Car", region="N/A"): # Added vehicle_type and region
        self.vehicle_id = vehicle_id
        self.name = name
        self.max_capacity = max_capacity
        self.odometer = odometer
        self.out_of_service = out_of_service
        self.acquisition_cost = acquisition_cost
        self.vehicle_type = vehicle_type # New field
        self.region = region # New field
        self.available = not out_of_service

class Driver(BaseModel):
    def __init__(self, driver_id, name, license_expiry="N/A", status=DriverStatus.OFF_DUTY, safety_score=100): # Updated
        self.driver_id = driver_id
        self.name = name
        self.license_expiry = license_expiry
        self.status = status # Using enum
        self.safety_score = safety_score # New field

    @property
    def available(self):
        if self.status != DriverStatus.ON_DUTY:
            return False
        if self.license_expiry == "N/A":
            return True # Assume N/A means valid or not applicable for expiry check
        
        try:
            expiry_date = datetime.strptime(self.license_expiry, "%Y-%m-%d").date()
            return expiry_date >= datetime.now().date()
        except ValueError:
            return False # Invalid date format, consider not available

class Trip(BaseModel):
    def __init__(self, vehicle_id, driver_id, cargo_weight, status=TripStatus.DRAFT, trip_id=None, start_odometer=0.0, end_odometer=0.0): # Updated
        self.trip_id = trip_id if trip_id is not None else str(uuid.uuid4()) # Generate unique ID
        self.vehicle_id = vehicle_id
        self.driver_id = driver_id
        self.cargo_weight = cargo_weight
        self.status = status
        self.start_odometer = start_odometer # New field
        self.end_odometer = end_odometer # New field
        self.start_time = datetime.now().isoformat()
        self.end_time = None

class MaintenanceLog(BaseModel):
    def __init__(self, vehicle_id, description, cost, date=None, status="Open", log_id=None):
        self.log_id = log_id if log_id is not None else str(uuid.uuid4())
        self.vehicle_id = vehicle_id
        self.description = description
        self.cost = cost
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")
        self.status = status

class FuelLog(BaseModel):
    def __init__(self, vehicle_id, liters, cost, date=None, log_id=None):
        self.log_id = log_id if log_id is not None else str(uuid.uuid4())
        self.vehicle_id = vehicle_id
        self.liters = liters
        self.cost = cost
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")

class FleetDataModel:
    def __init__(self, load_defaults=True, data_manager=None):
        self.data_manager = data_manager if data_manager else FleetDataManager()
        self.load_defaults = load_defaults # Store load_defaults as an instance variable
        self._users = {}
        self._vehicles = {}
        self._drivers = {}
        self._trips = {}
        self._maintenance_logs = {}
        self._fuel_logs = {} # Initialize fuel logs

        self._next_trip_id = 1 # Simple ID generation for now, will use UUIDs

        self._load_all_entities()

    def _load_all_entities(self):
        # Load users
        users_data = self.data_manager.get_entity_data("users")
        for email, user_dict in users_data.items():
            self._users[email] = User.from_dict(user_dict)

        # Load vehicles
        vehicles_data = self.data_manager.get_entity_data("vehicles")
        for vehicle_id, vehicle_dict in vehicles_data.items():
            self._vehicles[vehicle_id] = Vehicle.from_dict(vehicle_dict)

        # Load drivers
        drivers_data = self.data_manager.get_entity_data("drivers")
        for driver_id, driver_dict in drivers_data.items():
            self._drivers[driver_id] = Driver.from_dict(driver_dict)

        # Load trips
        trips_data = self.data_manager.get_entity_data("trips")
        for trip_id, trip_dict in trips_data.items():
            self._trips[trip_id] = Trip.from_dict(trip_dict)

        # Load maintenance logs
        maintenance_logs_data = self.data_manager.get_entity_data("maintenance_logs")
        for log_id, log_dict in maintenance_logs_data.items():
            self._maintenance_logs[log_id] = MaintenanceLog.from_dict(log_dict)

        # Load fuel logs
        fuel_logs_data = self.data_manager.get_entity_data("fuel_logs")
        for log_id, log_dict in fuel_logs_data.items():
            self._fuel_logs[log_id] = FuelLog.from_dict(log_dict)

        # Initialize default users if none exist
        if self.load_defaults and not self._users:
            self.add_user(User("manager@fleetflow.com", "admin123", "Manager"))
            self.add_user(User("dispatcher@fleetflow.com", "dispatch123", "Dispatcher"))
            self.add_user(User("safety@fleetflow.com", "safety123", "Safety"))
            self.add_user(User("finance@fleetflow.com", "finance123", "Finance"))
            self._save_all_entities()


    def _save_all_entities(self):
        all_data = {
            "users": {email: user.to_dict() for email, user in self._users.items()},
            "vehicles": {vehicle_id: vehicle.to_dict() for vehicle_id, vehicle in self._vehicles.items()},
            "drivers": {driver_id: driver.to_dict() for driver_id, driver in self._drivers.items()},
            "trips": {trip_id: trip.to_dict() for trip_id, trip in self._trips.items()},
            "maintenance_logs": {log_id: log.to_dict() for log_id, log in self._maintenance_logs.items()},
            "fuel_logs": {log_id: log.to_dict() for log_id, log in self._fuel_logs.items()} # Save fuel logs
        }
        self.data_manager.save_all_data(all_data)

    # --- User Management ---
    def get_user(self, email):
        return self._users.get(email)

    def add_user(self, user):
        self._users[user.email] = user
        self._save_all_entities()

    # --- Vehicle Management ---
    def get_vehicle(self, vehicle_id):
        return self._vehicles.get(vehicle_id)

    def get_all_vehicles(self):
        return list(self._vehicles.values())

    def add_vehicle(self, vehicle):
        if vehicle.vehicle_id in self._vehicles:
            raise ValueError(f"Vehicle with ID {vehicle.vehicle_id} already exists.")
        self._vehicles[vehicle.vehicle_id] = vehicle
        self._save_all_entities()

    def update_vehicle(self, vehicle_id, **kwargs):
        vehicle = self.get_vehicle(vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle with ID {vehicle_id} not found.")
        for key, value in kwargs.items():
            setattr(vehicle, key, value)
        self._save_all_entities()

    def delete_vehicle(self, vehicle_id):
        if vehicle_id in self._vehicles:
            del self._vehicles[vehicle_id]
            self._save_all_entities()

    # --- Driver Management ---
    def get_driver(self, driver_id):
        return self._drivers.get(driver_id)

    def get_all_drivers(self):
        return list(self._drivers.values())

    def add_driver(self, driver):
        if driver.driver_id in self._drivers:
            raise ValueError(f"Driver with ID {driver.driver_id} already exists.")
        self._drivers[driver.driver_id] = driver
        self._save_all_entities()

    def update_driver(self, driver_id, **kwargs):
        driver = self.get_driver(driver_id)
        if not driver:
            raise ValueError(f"Driver with ID {driver_id} not found.")
        for key, value in kwargs.items():
            setattr(driver, key, value)
        self._save_all_entities()

    def delete_driver(self, driver_id):
        if driver_id in self._drivers:
            del self._drivers[driver_id]
            self._save_all_entities()

    # --- Trip Management ---
    def get_trip(self, trip_id):
        return self._trips.get(trip_id)

    def get_all_trips(self):
        return list(self._trips.values())

    def add_trip(self, trip):
        # Business Rule: Prevent trip creation if CargoWeight > MaxCapacity
        vehicle = self.get_vehicle(trip.vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {trip.vehicle_id} not found for trip.")
        if trip.cargo_weight > vehicle.max_capacity:
            raise ValueError("Cargo weight exceeds vehicle capacity!")

        # Business Rule: Prevent trip creation if driver's license is expired
        driver = self.get_driver(trip.driver_id)
        if driver:
            # Assuming license_expiry is in "YYYY-MM-DD" format
            if driver.license_expiry != "N/A" and datetime.strptime(driver.license_expiry, "%Y-%m-%d").date() < datetime.now().date():
                raise ValueError(f"Driver {driver.name}'s license is expired. Cannot assign trip.")

        # Update vehicle and driver availability
        vehicle.available = False # This is fine as vehicle.available is not a property
        if driver:
            driver.status = DriverStatus.ON_DUTY # Driver is now on duty for the trip
            # The 'available' property of driver will now correctly reflect its status and license expiry
            # self.update_driver already handles saving, but ensure status is passed
            self.update_driver(driver.driver_id, status=DriverStatus.ON_DUTY)

        self._trips[trip.trip_id] = trip
        self._save_all_entities()

    def update_trip_status(self, trip_id, new_status, end_odometer=None): # Added end_odometer
        trip = self.get_trip(trip_id)
        if not trip:
            raise ValueError(f"Trip with ID {trip_id} not found.")

        old_status = trip.status

        # Enforce lifecycle
        if new_status == TripStatus.DISPATCHED:
            if old_status != TripStatus.DRAFT:
                raise ValueError("Trip can only be dispatched from Draft status.")
            # Mark associated vehicle as unavailable
            vehicle = self.get_vehicle(trip.vehicle_id)
            if vehicle:
                vehicle.available = False
                self.update_vehicle(vehicle.vehicle_id, available=False)
        elif new_status == TripStatus.COMPLETED:
            if old_status != TripStatus.DISPATCHED:
                raise ValueError("Trip can only be completed from Dispatched status.")
            if end_odometer is None:
                raise ValueError("End odometer is required to complete a trip.")
            if end_odometer < trip.start_odometer:
                raise ValueError("End odometer cannot be less than start odometer.")
            trip.end_odometer = end_odometer
            # Update vehicle's current odometer
            vehicle = self.get_vehicle(trip.vehicle_id)
            if vehicle:
                vehicle.odometer = end_odometer
                self.update_vehicle(vehicle.vehicle_id, odometer=end_odometer) # Persist vehicle odometer change
        elif new_status == TripStatus.CANCELLED and old_status not in [TripStatus.DRAFT, TripStatus.DISPATCHED]:
            raise ValueError("Trip can only be cancelled from Draft or Dispatched status.")

        trip.status = new_status
        if new_status in [TripStatus.COMPLETED, TripStatus.CANCELLED]:
            trip.end_time = datetime.now().isoformat()
            self._release_vehicle_and_driver(trip)
        
        self._save_all_entities()

    def _release_vehicle_and_driver(self, trip):
        vehicle = self.get_vehicle(trip.vehicle_id)
        if vehicle:
            vehicle.available = True # This is fine as vehicle.available is not a property
        driver = self.get_driver(trip.driver_id)
        if driver:
            driver.status = DriverStatus.OFF_DUTY # Driver is now off duty after trip
            # The 'available' property of driver will now correctly reflect its status and license expiry
            self.update_driver(driver.driver_id, status=DriverStatus.OFF_DUTY)
        self._save_all_entities()

    # --- Maintenance Log Management ---
    def get_maintenance_log(self, log_id):
        return self._maintenance_logs.get(log_id)

    def get_all_maintenance_logs(self):
        return list(self._maintenance_logs.values())

    def add_maintenance_log(self, log):
        if log.log_id in self._maintenance_logs:
            raise ValueError(f"Maintenance log with ID {log.log_id} already exists.")
        
        # Business Rule: Vehicle status changes to "In Shop"
        vehicle = self.get_vehicle(log.vehicle_id)
        if vehicle:
            # Check if vehicle is already in shop, if not, update status
            if not vehicle.out_of_service:
                vehicle.out_of_service = True
                vehicle.available = False
                self.update_vehicle(vehicle.vehicle_id, out_of_service=True, available=False)
            else:
                # If vehicle is already out of service, just add the log
                pass
        
        self._maintenance_logs[log.log_id] = log
        self._save_all_entities()

    def update_maintenance_log_status(self, log_id, new_status):
        log = self.get_maintenance_log(log_id)
        if not log:
            raise ValueError(f"Maintenance log with ID {log_id} not found.")
        
        log.status = new_status
        
        # Business Rule: If completed, vehicle status changes to "Available"
        if new_status == "Completed":
            vehicle = self.get_vehicle(log.vehicle_id)
            if vehicle:
                # Only set to available if no other active "Open" maintenance logs exist for this vehicle
                active_logs = [l for l in self._maintenance_logs.values() 
                               if l.vehicle_id == log.vehicle_id and l.status == "Open" and l.log_id != log_id]
                if not active_logs:
                    vehicle.out_of_service = False
                    vehicle.available = True
                    self.update_vehicle(vehicle.vehicle_id, out_of_service=False, available=True)
                else: # If update_vehicle was not called, we still need to save the log's status change
                    self._save_all_entities()
        else: # If new_status is not "Completed", we still need to save the log's status change
            self._save_all_entities()

    # --- Fuel Log Management ---
    def get_fuel_log(self, log_id):
        return self._fuel_logs.get(log_id)

    def get_all_fuel_logs(self):
        return list(self._fuel_logs.values())

    def add_fuel_log(self, log):
        if log.log_id in self._fuel_logs:
            raise ValueError(f"Fuel log with ID {log.log_id} already exists.")
        self._fuel_logs[log.log_id] = log
        self._save_all_entities()

import uuid # Import uuid for generating unique IDs
