import pytest
import os
from unittest.mock import MagicMock, patch
from fleetflow.fleet_data_model import FleetDataModel, User, Vehicle, Driver, Trip, MaintenanceLog, FuelLog, TripStatus, DriverStatus
from datetime import datetime, timedelta

# Mock FleetDataManager to prevent actual file I/O during tests
@pytest.fixture
def mock_data_manager():
    with patch('fleetflow.data_manager.FleetDataManager', autospec=True) as MockDataManager:
        manager_instance = MockDataManager.return_value
        manager_instance.get_entity_data.side_effect = lambda entity_type: {} # Default to empty data
        yield manager_instance

@pytest.fixture
def empty_fleet_data_model(mock_data_manager):
    model = FleetDataModel(load_defaults=False, data_manager=mock_data_manager)
    # Ensure no default users are created during test setup
    model._users = {}
    model._vehicles = {}
    model._drivers = {}
    model._trips = {}
    model._maintenance_logs = {}
    model._fuel_logs = {}
    return model

@pytest.fixture
def populated_fleet_data_model(mock_data_manager):
    # Define the data that the mock manager will return
    _test_users = {
        "manager@test.com": User("manager@test.com", "pass", "Manager"),
        "dispatcher@test.com": User("dispatcher@test.com", "pass", "Dispatcher"),
    }
    _test_vehicles = {
        "V001": Vehicle("V001", 1000, "Truck", 10000, False, 50000.0, "Truck", "North"),
        "V002": Vehicle("V002", 500, "Van", 5000, True, 25000.0, "Van", "South"), # Out of service
    }
    _test_drivers = {
        "D001": Driver("D001", "Alice", (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), DriverStatus.ON_DUTY, 90), # Available
        "D002": Driver("D002", "Bob", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), DriverStatus.ON_DUTY, 80), # Expired license
        "D003": Driver("D003", "Charlie", (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), DriverStatus.OFF_DUTY, 95), # Off duty
    }
    _test_trips = {
        "T001": Trip("V001", "D001", 200, TripStatus.DRAFT, "T001", 10000.0),
        "T002": Trip("V001", "D001", 150, TripStatus.DISPATCHED, "T002", 10200.0),
    }
    _test_maintenance_logs = {
        # "M001": MaintenanceLog("V001", "Oil Change", 100.0, datetime.now().strftime("%Y-%m-%d")),
    } # Removed pre-populated maintenance log to avoid test interference
    _test_fuel_logs = {
        "F001": FuelLog("V001", 50.0, 75.0, datetime.now().strftime("%Y-%m-%d")),
    }

    mock_data_manager.get_entity_data.side_effect = lambda entity_type: {
        "users": {e: u.to_dict() for e, u in _test_users.items()},
        "vehicles": {vid: v.to_dict() for vid, v in _test_vehicles.items()},
        "drivers": {did: d.to_dict() for did, d in _test_drivers.items()},
        "trips": {tid: t.to_dict() for tid, t in _test_trips.items()},
        "maintenance_logs": {mid: ml.to_dict() for mid, ml in _test_maintenance_logs.items()},
        "fuel_logs": {fid: fl.to_dict() for fid, fl in _test_fuel_logs.items()},
    }.get(entity_type, {})

    model = FleetDataModel(load_defaults=False, data_manager=mock_data_manager) # Instantiate AFTER mock is configured

    # Manually assign the pre-defined data to the model's internal dictionaries
    # This prevents side effects from add_user/add_vehicle etc. during setup
    model._users = _test_users
    model._vehicles = _test_vehicles
    model._drivers = _test_drivers
    model._trips = _test_trips
    model._maintenance_logs = _test_maintenance_logs
    model._fuel_logs = _test_fuel_logs
    
    # Reset the mock after initial setup in the fixture to clear any calls from __init__ or _load_all_entities
    mock_data_manager.save_all_data.reset_mock()
    return model

class TestFleetDataModel:

    def test_initial_state(self, empty_fleet_data_model):
        model = empty_fleet_data_model
        assert not list(model._users.values())
        assert not model.get_all_vehicles()
        assert not model.get_all_drivers()
        assert not model.get_all_trips()

    # --- User Management Tests ---
    def test_add_user(self, empty_fleet_data_model, mock_data_manager):
        model = empty_fleet_data_model
        user = User("test@test.com", "pass", "Manager")
        model.add_user(user)
        assert model.get_user("test@test.com") == user
        mock_data_manager.save_all_data.assert_called_once()

    def test_get_user(self, populated_fleet_data_model):
        model = populated_fleet_data_model
        user = model.get_user("manager@test.com")
        assert user is not None
        assert user.email == "manager@test.com"

    # --- Vehicle Management Tests ---
    def test_add_vehicle(self, empty_fleet_data_model, mock_data_manager):
        model = empty_fleet_data_model
        vehicle = Vehicle("V003", 1200, "Bus", 15000, False, 70000.0, "Bus", "East")
        model.add_vehicle(vehicle)
        assert model.get_vehicle("V003") == vehicle
        mock_data_manager.save_all_data.assert_called_once()

    def test_add_duplicate_vehicle_raises_error(self, populated_fleet_data_model):
        model = populated_fleet_data_model
        vehicle = Vehicle("V001", 1000, "Truck", 10000)
        with pytest.raises(ValueError, match="Vehicle with ID V001 already exists."):
            model.add_vehicle(vehicle)

    def test_update_vehicle(self, populated_fleet_data_model, mock_data_manager):
        model = populated_fleet_data_model
        model.update_vehicle("V001", odometer=11000, out_of_service=True)
        updated_vehicle = model.get_vehicle("V001")
        assert updated_vehicle.odometer == 11000
        assert updated_vehicle.out_of_service is True
        mock_data_manager.save_all_data.assert_called_once()

    def test_update_nonexistent_vehicle_raises_error(self, empty_fleet_data_model):
        model = empty_fleet_data_model
        with pytest.raises(ValueError, match="Vehicle with ID VXXX not found."):
            model.update_vehicle("VXXX", odometer=100)

    def test_delete_vehicle(self, populated_fleet_data_model, mock_data_manager):
        model = populated_fleet_data_model
        model.delete_vehicle("V001")
        assert model.get_vehicle("V001") is None
        mock_data_manager.save_all_data.assert_called_once()

    def test_delete_nonexistent_vehicle_no_error(self, empty_fleet_data_model):
        model = empty_fleet_data_model
        model.delete_vehicle("VXXX") # Should not raise error
        assert model.get_vehicle("VXXX") is None

    # --- Driver Management Tests ---
    def test_add_driver(self, empty_fleet_data_model, mock_data_manager):
        model = empty_fleet_data_model
        driver = Driver("D004", "David", "2025-01-01", DriverStatus.OFF_DUTY)
        model.add_driver(driver)
        assert model.get_driver("D004") == driver
        mock_data_manager.save_all_data.assert_called_once()

    def test_add_duplicate_driver_raises_error(self, populated_fleet_data_model):
        model = populated_fleet_data_model
        driver = Driver("D001", "Alice", "2025-01-01", DriverStatus.ON_DUTY)
        with pytest.raises(ValueError, match="Driver with ID D001 already exists."):
            model.add_driver(driver)

    def test_update_driver(self, populated_fleet_data_model, mock_data_manager):
        model = populated_fleet_data_model
        model.update_driver("D001", status=DriverStatus.OFF_DUTY, safety_score=95)
        updated_driver = model.get_driver("D001")
        assert updated_driver.status == DriverStatus.OFF_DUTY
        assert updated_driver.safety_score == 95
        assert updated_driver.available is False # Should be false as status is OFF_DUTY
        mock_data_manager.save_all_data.assert_called_once()

    def test_driver_available_property(self, populated_fleet_data_model):
        model = populated_fleet_data_model
        # D001: ON_DUTY, license valid
        driver1 = model.get_driver("D001")
        assert driver1.available is True
        
        # D002: ON_DUTY, license expired
        driver2 = model.get_driver("D002")
        assert driver2.available is False
        
        # D003: OFF_DUTY, license valid
        driver3 = model.get_driver("D003")
        assert driver3.available is False

    # --- Trip Management Tests ---
    def test_add_trip_success(self, populated_fleet_data_model, mock_data_manager):
        model = populated_fleet_data_model
        # Make V001 available (from being DISPATCHED)
        model.get_vehicle("V001").available = True
        model.get_driver("D001").status = DriverStatus.ON_DUTY
        model.get_driver("D001").license_expiry = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        trip = Trip("V001", "D001", 500, TripStatus.DRAFT, "T003", 10500.0)
        model.add_trip(trip)
        assert model.get_trip("T003") == trip
        # Check vehicle and driver status updates
        assert model.get_vehicle("V001").available is False
        assert model.get_driver("D001").status == DriverStatus.ON_DUTY
        assert model.get_driver("D001").available is True # Driver is ON_DUTY and license is valid
        mock_data_manager.save_all_data.assert_called()

    def test_add_trip_exceeds_capacity(self, populated_fleet_data_model):
        model = populated_fleet_data_model
        # Make V001 available
        model.get_vehicle("V001").available = True
        with pytest.raises(ValueError, match="Cargo weight exceeds vehicle capacity!"):
            model.add_trip(Trip("V001", "D001", 1200, TripStatus.DRAFT, "T004"))

    def test_add_trip_driver_license_expired(self, populated_fleet_data_model):
        model = populated_fleet_data_model
        # Make V001 available
        model.get_vehicle("V001").available = True
        # D002 has expired license in fixture
        with pytest.raises(ValueError, match="Driver Bob's license is expired. Cannot assign trip."):
            model.add_trip(Trip("V001", "D002", 200, TripStatus.DRAFT, "T005"))

    def test_update_trip_status_to_dispatched(self, populated_fleet_data_model, mock_data_manager):
        model = populated_fleet_data_model
        # Set V001 to available to allow dispatching the DRAFT T001
        # Vehicle V001 is already available=True from fixture setup (out_of_service=False)
        # add_trip will set it to available=False. No need to explicitly set here.
        model.get_driver("D001").status = DriverStatus.ON_DUTY
        model.get_driver("D001").license_expiry = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        model.update_trip_status("T001", TripStatus.DISPATCHED)
        trip = model.get_trip("T001")
        assert trip.status == TripStatus.DISPATCHED
        assert model.get_vehicle("V001").available is False
        assert model.get_driver("D001").status == DriverStatus.ON_DUTY
        assert model.get_driver("D001").available is True
        mock_data_manager.save_all_data.assert_called()

    def test_update_trip_status_to_completed(self, populated_fleet_data_model, mock_data_manager):
        model = populated_fleet_data_model
        model.update_trip_status("T002", TripStatus.COMPLETED, end_odometer=10500.0)
        trip = model.get_trip("T002")
        assert trip.status == TripStatus.COMPLETED
        assert trip.end_odometer == 10500.0
        assert model.get_vehicle("V001").odometer == 10500.0
        assert model.get_vehicle("V001").available is True # Vehicle released
        assert model.get_driver("D001").status == DriverStatus.OFF_DUTY # Driver released
        assert model.get_driver("D001").available is False # Driver is OFF_DUTY
        mock_data_manager.save_all_data.assert_called()

    def test_update_trip_status_invalid_transition(self, populated_fleet_data_model):
        model = populated_fleet_data_model
        with pytest.raises(ValueError, match="Trip can only be dispatched from Draft status."):
            model.update_trip_status("T002", TripStatus.DISPATCHED) # T002 is DISPATCHED, can't dispatch again

    def test_update_trip_status_completed_no_end_odometer(self, populated_fleet_data_model):
        model = populated_fleet_data_model
        with pytest.raises(ValueError, match="End odometer is required to complete a trip."):
            model.update_trip_status("T002", TripStatus.COMPLETED)

    # --- Maintenance Log Management Tests ---
    def test_add_maintenance_log(self, populated_fleet_data_model, mock_data_manager):
        model = populated_fleet_data_model
        # V001 is active
        log = MaintenanceLog("V001", "Tire Rotation", 50.0, "2024-03-01")
        model.add_maintenance_log(log)
        assert model.get_maintenance_log(log.log_id) == log
        # Check vehicle status
        vehicle = model.get_vehicle("V001")
        assert vehicle.out_of_service is True
        assert vehicle.available is False
        mock_data_manager.save_all_data.assert_called()

    def test_update_maintenance_log_status_to_completed(self, populated_fleet_data_model, mock_data_manager):
        model = populated_fleet_data_model
        # Add a maintenance log to V001 to put it out of service
        log = MaintenanceLog("V001", "Brake Check", 75.0, "2024-03-02")
        model.add_maintenance_log(log) # This will set V001 out of service
        mock_data_manager.save_all_data.reset_mock() # Reset mock call count

        # Complete the maintenance log
        model.update_maintenance_log_status(log.log_id, "Completed")
        updated_log = model.get_maintenance_log(log.log_id)
        assert updated_log.status == "Completed"
        # Check vehicle status - should be active again if no other open logs
        vehicle = model.get_vehicle("V001")
        assert vehicle.out_of_service is False
        assert vehicle.available is True
        mock_data_manager.save_all_data.assert_called_once()
    
    def test_update_maintenance_log_status_completed_other_open_logs(self, populated_fleet_data_model, mock_data_manager):
        model = populated_fleet_data_model
        # Add two maintenance logs to V001
        log1 = MaintenanceLog("V001", "Service A", 100.0, "2024-03-01")
        log2 = MaintenanceLog("V001", "Service B", 50.0, "2024-03-02")
        model.add_maintenance_log(log1)
        model.add_maintenance_log(log2) # V001 is now out of service due to log1, then log2
        mock_data_manager.save_all_data.reset_mock()

        # Complete log1
        model.update_maintenance_log_status(log1.log_id, "Completed")
        updated_log1 = model.get_maintenance_log(log1.log_id)
        assert updated_log1.status == "Completed"
        # Vehicle V001 should still be out of service because log2 is open
        vehicle = model.get_vehicle("V001")
        assert vehicle.out_of_service is True
        assert vehicle.available is False
        mock_data_manager.save_all_data.assert_called_once()


    # --- Fuel Log Management Tests ---
    def test_add_fuel_log(self, empty_fleet_data_model, mock_data_manager):
        model = empty_fleet_data_model
        log = FuelLog("V001", 30.0, 45.0, "2024-03-05")
        model.add_fuel_log(log)
        assert model.get_fuel_log(log.log_id) == log
        mock_data_manager.save_all_data.assert_called_once()
