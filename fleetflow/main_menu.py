import tkinter as tk
from fleetflow.theme import DARK_THEME, FONT_FAMILY
from fleetflow.vehicle_registry import VehicleRegistryUI
from fleetflow.trip_dispatcher import DispatcherApp
from fleetflow.maintenance_ui import MaintenancePage
from fleetflow.driver_registry_ui import DriverRegistryUI
from fleetflow.dashboard_ui import DashboardUI # Import DashboardUI
from fleetflow.fuel_log_ui import FuelLogUI # Import FuelLogUI
from fleetflow.analytics_reports_ui import AnalyticsReportsUI # Import AnalyticsReportsUI
from fleetflow.ui_components import BasePage # Import BasePage
from fleetflow.permissions import (
    has_permission,
    VEHICLE_REGISTRY_PERMISSIONS,
    TRIP_DISPATCHER_PERMISSIONS,
    DRIVER_REGISTRY_PERMISSIONS,
    MAINTENANCE_PERMISSIONS,
    FUEL_LOG_PERMISSIONS,
    ANALYTICS_PERMISSIONS,
    DASHBOARD_PERMISSIONS
)

class MainMenu(BasePage): # Inherit from BasePage
    def __init__(self, master, controller, fleet_data_model=None, user_role="Guest"): # Accept fleet_data_model
        super().__init__(master, controller, fleet_data_model, user_role) # Call BasePage.__init__
        self.master = master
        self.controller = controller
        self.user_role = user_role
        self.fleet_data_model = fleet_data_model # Store it

        self.create_widgets()

    def create_widgets(self):
        # Welcome message
        welcome_label = self.create_label(self,
                                 text=f"Welcome, {self.user_role}!",
                                 font_size=24, font_weight="bold")
        welcome_label.pack(pady=40)

        # Button Frame
        button_frame = tk.Frame(self, bg=DARK_THEME["bg"])
        button_frame.pack(pady=20, padx=100, fill="x")

        buttons_to_add = []
        
        # Open Dashboard Button
        if has_permission(self.user_role, DASHBOARD_PERMISSIONS["view"]):
            buttons_to_add.append((
                "Open Dashboard",
                lambda: self.open_module(DashboardUI, "Command Center Dashboard"),
                "Accent.TButton"
            ))

        # Open Vehicle Registry Button
        if has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["view"]):
            buttons_to_add.append((
                "Open Vehicle Registry",
                lambda: self.open_module(VehicleRegistryUI, "Vehicle Registry"),
                "Primary.TButton"
            ))

        # Open Driver Registry Button
        if has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["view"]):
            buttons_to_add.append((
                "Open Driver Registry",
                lambda: self.open_module(DriverRegistryUI, "Driver Registry"),
                "Info.TButton"
            ))

        # Open Trip Dispatcher Button
        if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["view"]):
            buttons_to_add.append((
                "Open Trip Dispatcher",
                lambda: self.open_module(DispatcherApp, "Trip Dispatcher"),
                "Highlight.TButton"
            ))
        
        # Open Maintenance Logs Button
        if has_permission(self.user_role, MAINTENANCE_PERMISSIONS["view"]):
            buttons_to_add.append((
                "Open Maintenance Logs",
                lambda: self.open_module(MaintenancePage, "Maintenance & Service Logs"),
                "Warning.TButton"
            ))

        # Open Fuel Logs Button (New)
        if has_permission(self.user_role, FUEL_LOG_PERMISSIONS["view"]):
            buttons_to_add.append((
                "Open Fuel Logs",
                lambda: self.open_module(FuelLogUI, "Fuel Logging"),
                "Primary.TButton"
            ))

        # Open Analytics & Reports Button (New)
        if has_permission(self.user_role, ANALYTICS_PERMISSIONS["view"]):
            buttons_to_add.append((
                "Open Analytics & Reports",
                lambda: self.open_module(AnalyticsReportsUI, "Operational Analytics & Financial Reports"),
                "Info.TButton"
            ))

        for text, command, style in buttons_to_add:
            btn = self.create_button(button_frame,
                                     text=text,
                                     command=command,
                                     style=style)
            btn.pack(pady=5, fill="x")

        # Logout Button
        logout_btn = self.create_button(self,
                               text="Logout",
                               command=self.controller.logout,
                               style="Danger.TButton")
        
        logout_btn.pack(side="bottom", pady=20, ipadx=10)
    def open_module(self, module_class, title):
        top_level = tk.Toplevel(self.master)
        top_level.title(title)
        top_level.geometry("1000x600") # Default size
        top_level.resizable(False, False) # Make the Toplevel window non-resizable
        # Pass fleet_data_model, controller, and user_role to the module
        module_class(top_level, self.controller, self.fleet_data_model, self.user_role)
