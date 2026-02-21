# Permissions for Vehicle Registry Module
VEHICLE_REGISTRY_PERMISSIONS = {
    "view": "can_view_vehicles",
    "add": "can_add_vehicles",
    "update": "can_update_vehicles",
    "delete": "can_delete_vehicles",
    "toggle_status": "can_toggle_vehicle_status",
    "view_stats": "can_view_vehicle_stats"
}

# Permissions for Trip Dispatcher Module
TRIP_DISPATCHER_PERMISSIONS = {
    "view": "can_view_trips",
    "create": "can_create_trips",
    "dispatch": "can_dispatch_trips",
    "complete": "can_complete_trips",
    "cancel": "can_cancel_trips"
}

# Permissions for Driver Registry Module
DRIVER_REGISTRY_PERMISSIONS = {
    "view": "can_view_drivers",
    "add": "can_add_drivers",
    "update": "can_update_drivers",
    "delete": "can_delete_drivers",
    "toggle_status": "can_toggle_driver_status" # For On Duty/Off Duty
}

# Permissions for Maintenance Logs Module
MAINTENANCE_PERMISSIONS = {
    "view": "can_view_maintenance",
    "add": "can_add_maintenance",
    "update": "can_update_maintenance", # For completing logs
    "delete": "can_delete_maintenance"
}

# Permissions for Fuel Logs Module
FUEL_LOG_PERMISSIONS = {
    "view": "can_view_fuel_logs",
    "add": "can_add_fuel_logs",
    "update": "can_update_fuel_logs", # Not implemented yet but placeholder
    "delete": "can_delete_fuel_logs" # Not implemented yet but placeholder
}

# Permissions for Analytics & Reports
ANALYTICS_PERMISSIONS = {
    "view": "can_view_analytics",
    "export": "can_export_reports"
}

# Permissions for Dashboard Module
DASHBOARD_PERMISSIONS = {
    "view": "can_view_dashboard"
}

# Role-based permissions mapping
ROLE_PERMISSIONS = {
    "Manager": {
        VEHICLE_REGISTRY_PERMISSIONS["view"]: True,
        VEHICLE_REGISTRY_PERMISSIONS["add"]: True,
        VEHICLE_REGISTRY_PERMISSIONS["update"]: True,
        VEHICLE_REGISTRY_PERMISSIONS["delete"]: True,
        VEHICLE_REGISTRY_PERMISSIONS["toggle_status"]: True,
        VEHICLE_REGISTRY_PERMISSIONS["view_stats"]: True,

        TRIP_DISPATCHER_PERMISSIONS["view"]: True,
        TRIP_DISPATCHER_PERMISSIONS["create"]: True,
        TRIP_DISPATCHER_PERMISSIONS["dispatch"]: True,
        TRIP_DISPATCHER_PERMISSIONS["complete"]: True,
        TRIP_DISPATCHER_PERMISSIONS["cancel"]: True,

        DRIVER_REGISTRY_PERMISSIONS["view"]: True,
        DRIVER_REGISTRY_PERMISSIONS["add"]: True,
        DRIVER_REGISTRY_PERMISSIONS["update"]: True,
        DRIVER_REGISTRY_PERMISSIONS["delete"]: True,
        DRIVER_REGISTRY_PERMISSIONS["toggle_status"]: True,

        MAINTENANCE_PERMISSIONS["view"]: True,
        MAINTENANCE_PERMISSIONS["add"]: True,
        MAINTENANCE_PERMISSIONS["update"]: True,
        MAINTENANCE_PERMISSIONS["delete"]: True,

        FUEL_LOG_PERMISSIONS["view"]: True,
        FUEL_LOG_PERMISSIONS["add"]: True,
        FUEL_LOG_PERMISSIONS["update"]: True,
        FUEL_LOG_PERMISSIONS["delete"]: True,

        ANALYTICS_PERMISSIONS["view"]: True,
        ANALYTICS_PERMISSIONS["export"]: True,

        DASHBOARD_PERMISSIONS["view"]: True,
    },
    "Dispatcher": {
        VEHICLE_REGISTRY_PERMISSIONS["view"]: True,
        VEHICLE_REGISTRY_PERMISSIONS["add"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["update"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["delete"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["toggle_status"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["view_stats"]: True,

        TRIP_DISPATCHER_PERMISSIONS["view"]: True,
        TRIP_DISPATCHER_PERMISSIONS["create"]: True,
        TRIP_DISPATCHER_PERMISSIONS["dispatch"]: True,
        TRIP_DISPATCHER_PERMISSIONS["complete"]: True,
        TRIP_DISPATCHER_PERMISSIONS["cancel"]: True,

        DRIVER_REGISTRY_PERMISSIONS["view"]: True,
        DRIVER_REGISTRY_PERMISSIONS["add"]: False,
        DRIVER_REGISTRY_PERMISSIONS["update"]: False,
        DRIVER_REGISTRY_PERMISSIONS["delete"]: False,
        DRIVER_REGISTRY_PERMISSIONS["toggle_status"]: False,

        MAINTENANCE_PERMISSIONS["view"]: True, # Dispatchers need to see maintenance status
        MAINTENANCE_PERMISSIONS["add"]: False,
        MAINTENANCE_PERMISSIONS["update"]: False,
        MAINTENANCE_PERMISSIONS["delete"]: False,

        FUEL_LOG_PERMISSIONS["view"]: True,
        FUEL_LOG_PERMISSIONS["add"]: True, # Dispatchers might add fuel logs
        FUEL_LOG_PERMISSIONS["update"]: True,
        FUEL_LOG_PERMISSIONS["delete"]: False,

        ANALYTICS_PERMISSIONS["view"]: True,
        ANALYTICS_PERMISSIONS["export"]: False,

        DASHBOARD_PERMISSIONS["view"]: True,
    },
    "Safety": {
        VEHICLE_REGISTRY_PERMISSIONS["view"]: True,
        VEHICLE_REGISTRY_PERMISSIONS["add"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["update"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["delete"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["toggle_status"]: True, # Safety might need to mark vehicles out of service
        VEHICLE_REGISTRY_PERMISSIONS["view_stats"]: True,

        TRIP_DISPATCHER_PERMISSIONS["view"]: True,
        TRIP_DISPATCHER_PERMISSIONS["create"]: False,
        TRIP_DISPATCHER_PERMISSIONS["dispatch"]: False,
        TRIP_DISPATCHER_PERMISSIONS["complete"]: False,
        TRIP_DISPATCHER_PERMISSIONS["cancel"]: False,

        DRIVER_REGISTRY_PERMISSIONS["view"]: True,
        DRIVER_REGISTRY_PERMISSIONS["add"]: False,
        DRIVER_REGISTRY_PERMISSIONS["update"]: False,
        DRIVER_REGISTRY_PERMISSIONS["delete"]: False,
        DRIVER_REGISTRY_PERMISSIONS["toggle_status"]: True, # Safety can toggle driver status

        MAINTENANCE_PERMISSIONS["view"]: True,
        MAINTENANCE_PERMISSIONS["add"]: True, # Safety can add maintenance logs for issues
        MAINTENANCE_PERMISSIONS["update"]: False,
        MAINTENANCE_PERMISSIONS["delete"]: False,

        FUEL_LOG_PERMISSIONS["view"]: True,
        FUEL_LOG_PERMISSIONS["add"]: False,
        FUEL_LOG_PERMISSIONS["update"]: False,
        FUEL_LOG_PERMISSIONS["delete"]: False,

        ANALYTICS_PERMISSIONS["view"]: True,
        ANALYTICS_PERMISSIONS["export"]: False,

        DASHBOARD_PERMISSIONS["view"]: True,
    },
    "Finance": {
        VEHICLE_REGISTRY_PERMISSIONS["view"]: True,
        VEHICLE_REGISTRY_PERMISSIONS["add"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["update"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["delete"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["toggle_status"]: False,
        VEHICLE_REGISTRY_PERMISSIONS["view_stats"]: True,

        TRIP_DISPATCHER_PERMISSIONS["view"]: True,
        TRIP_DISPATCHER_PERMISSIONS["create"]: False,
        TRIP_DISPATCHER_PERMISSIONS["dispatch"]: False,
        TRIP_DISPATCHER_PERMISSIONS["complete"]: False,
        TRIP_DISPATCHER_PERMISSIONS["cancel"]: False,

        DRIVER_REGISTRY_PERMISSIONS["view"]: True,
        DRIVER_REGISTRY_PERMISSIONS["add"]: False,
        DRIVER_REGISTRY_PERMISSIONS["update"]: False,
        DRIVER_REGISTRY_PERMISSIONS["delete"]: False,
        DRIVER_REGISTRY_PERMISSIONS["toggle_status"]: False,

        MAINTENANCE_PERMISSIONS["view"]: True,
        MAINTENANCE_PERMISSIONS["add"]: False,
        MAINTENANCE_PERMISSIONS["update"]: False,
        MAINTENANCE_PERMISSIONS["delete"]: False,

        FUEL_LOG_PERMISSIONS["view"]: True,
        FUEL_LOG_PERMISSIONS["add"]: True, # Finance might want to input fuel logs or audit
        FUEL_LOG_PERMISSIONS["update"]: True,
        FUEL_LOG_PERMISSIONS["delete"]: False,

        ANALYTICS_PERMISSIONS["view"]: True,
        ANALYTICS_PERMISSIONS["export"]: True,

        DASHBOARD_PERMISSIONS["view"]: True,
    }
}

def has_permission(role, permission):
    return ROLE_PERMISSIONS.get(role, {}).get(permission, False)
