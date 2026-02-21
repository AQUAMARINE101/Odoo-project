import tkinter as tk
from tkinter import ttk
from fleetflow.theme import DARK_THEME, FONT_FAMILY
from fleetflow.fleet_data_model import FleetDataModel, TripStatus # Import TripStatus
from fleetflow.permissions import has_permission, DASHBOARD_PERMISSIONS
from fleetflow.ui_components import BasePage # Import BasePage

class DashboardUI(BasePage): # Inherit from BasePage
    def __init__(self, master, controller, fleet_data_model, user_role="Guest"):
        super().__init__(master, controller, fleet_data_model, user_role) # Call BasePage.__init__

        self.configure(bg=DARK_THEME["bg"]) # Set background for the entire page

        # Check permission to view dashboard
        if not has_permission(self.user_role, DASHBOARD_PERMISSIONS["view"]):
            self.create_label(self, text="Access Denied: You do not have permission to view the Dashboard.",
                              font_size=16, font_weight="bold", fg=DARK_THEME["danger"]).pack(pady=50)
            return

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_ui()
        self.refresh_kpis()

        # Subscribe to relevant events to refresh KPIs
        self.subscribe("vehicle_updated", self.refresh_kpis)
        self.subscribe("driver_updated", self.refresh_kpis)
        self.subscribe("trip_updated", self.refresh_kpis)
        self.subscribe("maintenance_updated", self.refresh_kpis)
        self.subscribe("fuel_log_updated", self.refresh_kpis)
        # Add subscription for region update if applicable
        self.subscribe("region_updated", self.refresh_kpis) # Assuming a region_updated event


    def build_ui(self):
        self.pack(fill="both", expand=True)
        # Header
        header = self.create_label(self, text="📊 Command Center (Main Dashboard)",
                                   font_size=20, font_weight="bold")
        header.pack(pady=20)

        # Filters Frame
        filters_frame = ttk.Frame(self, style='Dashboard.TFrame')
        filters_frame.pack(pady=10)

        # Vehicle Type Filter
        self.create_label(filters_frame, text="Vehicle Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.vehicle_type_var = tk.StringVar(value="All")
        self.vehicle_type_combo = ttk.Combobox(filters_frame, textvariable=self.vehicle_type_var, state="readonly", width=15)
        unique_vehicle_types = sorted(list(set([v.vehicle_type for v in self.fleet_data_model.get_all_vehicles()])))
        self.vehicle_type_combo['values'] = ["All"] + unique_vehicle_types
        self.vehicle_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.vehicle_type_combo.bind("<<ComboboxSelected>>", self.refresh_kpis)

        # Status Filter (e.g., Active, Out of Service)
        self.create_label(filters_frame, text="Vehicle Status:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.vehicle_status_var = tk.StringVar(value="All")
        self.vehicle_status_combo = ttk.Combobox(filters_frame, textvariable=self.vehicle_status_var, state="readonly", width=15)
        self.vehicle_status_combo['values'] = ["All", "Active", "Out of Service"]
        self.vehicle_status_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.vehicle_status_combo.bind("<<ComboboxSelected>>", self.refresh_kpis)

        # Region Filter (New)
        self.create_label(filters_frame, text="Region:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.region_var = tk.StringVar(value="All")
        self.region_combo = ttk.Combobox(filters_frame, textvariable=self.region_var, state="readonly", width=15)
        unique_regions = sorted(list(set([v.region for v in self.fleet_data_model.get_all_vehicles()])))
        self.region_combo['values'] = ["All"] + unique_regions
        self.region_combo.grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        self.region_combo.bind("<<ComboboxSelected>>", self.refresh_kpis)

        # KPIs Frame
        kpis_frame = ttk.Frame(self, style='Dashboard.TFrame')
        kpis_frame.pack(pady=20, fill="x", expand=True, padx=20)
        kpis_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)


        self.kpi_labels = {}
        kpis = [
            ("Active Fleet", "primary"),
            ("Maintenance Alerts", "danger"),
            ("Utilization Rate", "accent"),
            ("Pending Cargo", "warning")
        ]

        for i, (text, color_name) in enumerate(kpis):
            frame = ttk.Frame(kpis_frame, style='KpiCard.TFrame') # Use styled frame
            frame.grid(row=0, column=i, padx=15, pady=10, sticky="nsew") # Added internal padding
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_rowconfigure(1, weight=1)
            frame.grid_columnconfigure(0, weight=1)


            title = self.create_label(frame, text=text, font_size=12, font_weight="bold",
                                      style="KpiCardTitle.TLabel")
            title.grid(row=0, column=0, padx=20, pady=5)
            title.configure(foreground=DARK_THEME[color_name])

            value = self.create_label(frame, text="N/A", font_size=24, font_weight="bold",
                                      style="KpiCardValue.TLabel")
            value.grid(row=1, column=0, padx=20, pady=10)
            self.kpi_labels[text] = value
        
        # Back button
        self.create_back_button(self).pack(side="bottom", pady=10)


    def refresh_kpis(self, *args):
        selected_vehicle_type = self.vehicle_type_var.get()
        selected_vehicle_status = self.vehicle_status_var.get()
        selected_region = self.region_var.get() # Get selected region

        all_vehicles = self.fleet_data_model.get_all_vehicles()
        all_trips = self.fleet_data_model.get_all_trips()

        # Apply vehicle type filter
        if selected_vehicle_type != "All":
            filtered_vehicles_by_type = [v for v in all_vehicles if v.vehicle_type == selected_vehicle_type]
        else:
            filtered_vehicles_by_type = all_vehicles

        # Apply vehicle status filter
        if selected_vehicle_status != "All":
            if selected_vehicle_status == "Active":
                filtered_vehicles_by_status = [v for v in filtered_vehicles_by_type if not v.out_of_service]
            else: # Out of Service
                filtered_vehicles_by_status = [v for v in filtered_vehicles_by_type if v.out_of_service]
        else:
            filtered_vehicles_by_status = filtered_vehicles_by_type
        
        # Apply region filter
        filtered_vehicles = []
        for v in filtered_vehicles_by_status:
            if selected_region != "All":
                if v.region == selected_region:
                    filtered_vehicles.append(v)
            elif selected_region == "All":
                filtered_vehicles.append(v)

        # Filter trips based on the filtered vehicles
        filtered_vehicle_ids = {v.vehicle_id for v in filtered_vehicles}
        filtered_trips = [t for t in all_trips if t.vehicle_id in filtered_vehicle_ids]

        # Active Fleet: Count of vehicles currently "On Trip."
        active_trips = [t for t in filtered_trips if t.status == TripStatus.DISPATCHED]
        active_fleet_count = len({t.vehicle_id for t in active_trips}) # Unique vehicles on active trips
        self.kpi_labels["Active Fleet"].config(text=str(active_fleet_count))

        # Maintenance Alerts: Number of vehicles marked "In Shop."
        in_shop_vehicles = [v for v in filtered_vehicles if v.out_of_service]
        maintenance_alert_count = len(in_shop_vehicles)
        self.kpi_labels["Maintenance Alerts"].config(text=str(maintenance_alert_count))

        # Utilization Rate: % of fleet assigned vs. idle.
        total_filtered_vehicles = len(filtered_vehicles) # Use final filtered vehicles
        if total_filtered_vehicles > 0:
            assigned_vehicles = len({t.vehicle_id for t in filtered_trips if t.status == TripStatus.DISPATCHED or t.status == TripStatus.DRAFT}) # Consider both dispatched and draft as assigned
            utilization_rate = (assigned_vehicles / total_filtered_vehicles) * 100
            self.kpi_labels["Utilization Rate"].config(text=f"{utilization_rate:.1f}%")
        else:
            self.kpi_labels["Utilization Rate"].config(text="0.0%")
        
        # Pending Cargo: Shipments waiting for assignment (e.g., trips in Draft status)
        pending_cargo_count = len([t for t in filtered_trips if t.status == TripStatus.DRAFT])
        self.kpi_labels["Pending Cargo"].config(text=str(pending_cargo_count))

