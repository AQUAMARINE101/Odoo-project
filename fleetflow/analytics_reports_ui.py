import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta # Import timedelta
import csv # For CSV export

from fleetflow.theme import DARK_THEME, LIGHT_THEME, FONT_FAMILY
from fleetflow.permissions import has_permission, ANALYTICS_PERMISSIONS # Ensure correct permissions are imported
from fleetflow.fleet_data_model import FleetDataModel, Vehicle, Trip, MaintenanceLog, FuelLog, TripStatus # Import all relevant models
from fleetflow.ui_components import BasePage # Import BasePage

# Define permissions for Analytics & Reports
# ANALYTICS_PERMISSIONS is already defined, just re-referencing it here for clarity
# ANALYTICS_PERMISSIONS = {
#     "view": "can_view_analytics",
#     "export": "can_export_reports"
# }

class AnalyticsReportsUI(BasePage):
    def __init__(self, master, controller, fleet_data_model, user_role="Guest"):
        super().__init__(master, controller, fleet_data_model, user_role)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_ui()
        self.refresh_vehicle_filter_dropdown() # Initial population for vehicle filter
        self.update_report_data() # Initial report generation

        # Subscribe to relevant events to refresh reports
        self.controller.subscribe("vehicle_updated", self.refresh_vehicle_filter_dropdown) # Vehicle updates affect dropdown
        self.controller.subscribe("vehicle_updated", self.update_report_data)
        self.controller.subscribe("trip_updated", self.update_report_data)
        self.controller.subscribe("maintenance_updated", self.update_report_data)
        self.controller.subscribe("fuel_log_updated", self.update_report_data)
    

    # --------------------------------------------
    # UI Construction
    # --------------------------------------------
    def build_ui(self):
        self.pack(fill="both", expand=True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0) # Row for back button

        # Header
        self.create_label(self,
                 text="📈 Operational Analytics & Financial Reports",
                 font_size=18, font_weight="bold").grid(row=0, column=0,
                               columnspan=2, sticky="ew", pady=12, padx=10)

        self.build_filters_panel(self)
        self.build_reports_panel(self)
        
        # Back button
        self.create_back_button(self).grid(row=2, column=0, columnspan=2, pady=10)

    def build_filters_panel(self, parent_frame):
        filter_frame = ttk.Frame(parent_frame, style='AnalyticsCard.TFrame')
        filter_frame.grid(row=1, column=0, sticky="ns", padx=15, pady=15)
        filter_frame.grid_columnconfigure(1, weight=1)

        row_idx = 0

        self.create_label(filter_frame, text="Report Filters", font_size=12, font_weight="bold", style='AnalyticsCard.TLabel').grid(row=row_idx, column=0, columnspan=2, pady=(0,5), sticky="w")
        row_idx += 1

        # Vehicle Filter
        self.create_label(filter_frame, text="Select Vehicle (Optional)", style='AnalyticsCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.vehicle_filter_var = tk.StringVar()
        self.vehicle_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.vehicle_filter_var,
            state="readonly"
        )
        self.vehicle_filter_combo.grid(row=row_idx, column=1, padx=5, pady=(0,5), sticky="ew")
        self.vehicle_filter_combo.bind("<<ComboboxSelected>>", self.update_report_data)
        row_idx += 1

        # Date Range Filter
        self.create_label(filter_frame, text="Start Date (YYYY-MM-DD)", style='AnalyticsCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.start_date_entry = ttk.Entry(filter_frame)
        self.start_date_entry.grid(row=row_idx, column=1, padx=5, pady=(0,2), sticky="ew")
        self.start_date_entry.insert(0, (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d"))
        row_idx += 1

        self.create_label(filter_frame, text="End Date (YYYY-MM-DD)", style='AnalyticsCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.end_date_entry = ttk.Entry(filter_frame)
        self.end_date_entry.grid(row=row_idx, column=1, padx=5, pady=(0,5), sticky="ew")
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        row_idx += 1

        # Generate Report Button
        self.create_button(filter_frame, text="Generate Report", command=self.update_report_data, style="Primary.TButton").grid(row=row_idx, column=0, columnspan=2, pady=15, sticky="ew")
        row_idx += 1

        # Export Button
        self.create_button(filter_frame, text="Export to CSV", command=self.export_report_csv, style="Highlight.TButton",
                           state="normal" if has_permission(self.user_role, ANALYTICS_PERMISSIONS["export"]) else "disabled").grid(row=row_idx, column=0, columnspan=2, pady=5, sticky="ew")
        row_idx += 1
        
        # Placeholder for revenue assumption note
        self.create_label(filter_frame, text="*Vehicle ROI uses a fixed revenue assumption for demonstration purposes.",
                          font_size=8, style="AnalyticsCard.TLabel").grid(row=row_idx, column=0, columnspan=2, pady=(10,0), sticky="w")

    def build_reports_panel(self, parent_frame):
        reports_frame = ttk.Frame(parent_frame, style='AnalyticsCard.TFrame')
        reports_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=15)
        reports_frame.grid_columnconfigure(0, weight=1)
        reports_frame.grid_columnconfigure(1, weight=1)

        row_idx = 0

        self.create_label(reports_frame, text="Key Metrics", font_size=14, font_weight="bold", style='AnalyticsCard.TLabel').grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=(0,5))
        row_idx += 1

        self.metrics_labels = {}
        metrics_order = ["Total Operational Cost", "Total Distance Covered", "Total Fuel Consumed", "Fuel Efficiency (km/L)", "Vehicle ROI"]
        for metric in metrics_order:
            self.create_label(reports_frame, text=f"{metric}:", style='MetricName.TLabel').grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            value_label = self.create_label(reports_frame, text="N/A", style='MetricValue.TLabel')
            value_label.grid(row=row_idx, column=1, padx=5, pady=2, sticky="e")
            self.metrics_labels[metric] = value_label
            row_idx += 1

        self.create_label(reports_frame, text="Detailed Report (Table View)", font_size=14, font_weight="bold", style='AnalyticsCard.TLabel').grid(row=row_idx, column=0, columnspan=2, sticky="w", pady=(10,5))
        row_idx += 1

        # Table for detailed reports (e.g., per-vehicle breakdown)
        columns = ("Vehicle ID", "Distance (km)", "Fuel (L)", "Fuel Cost", "Maintenance Cost", "Total Cost", "Fuel Efficiency (km/L)", "ROI")
        self.report_tree = ttk.Treeview(reports_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, anchor="center", width=100)
        
        self.report_tree.column("Vehicle ID", width=80)
        self.report_tree.column("Distance (km)", width=90)
        self.report_tree.column("Fuel (L)", width=70)
        self.report_tree.column("Fuel Cost", width=80)
        self.report_tree.column("Maintenance Cost", width=110)
        self.report_tree.column("Total Cost", width=90)
        self.report_tree.column("Fuel Efficiency (km/L)", width=120)
        self.report_tree.column("ROI", width=70)

        self.report_tree.grid(row=row_idx, column=0, columnspan=2, sticky="nsew", pady=(0,10))
        reports_frame.grid_rowconfigure(row_idx, weight=1)

    # --------------------------------------------
    # Report Generation Logic
    # --------------------------------------------
    def refresh_vehicle_filter_dropdown(self, *args):
        all_vehicles = ["All Vehicles"] + [v.vehicle_id for v in self.fleet_data_model.get_all_vehicles()]
        self.vehicle_filter_combo["values"] = all_vehicles
        # Ensure the selected value is still valid, or reset to "All Vehicles"
        if self.vehicle_filter_var.get() not in all_vehicles:
            self.vehicle_filter_var.set("All Vehicles")


    def update_report_data(self, *args):
        if not has_permission(self.user_role, ANALYTICS_PERMISSIONS["view"]):
            # Do not show error if just refreshing from subscription, only if explicit view attempt
            # messagebox.showerror("Permission Denied", "You do not have permission to view analytics.")
            return

        selected_vehicle_id = self.vehicle_filter_var.get()
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date.")
        except ValueError as e:
            messagebox.showerror("Invalid Date", f"Invalid date format or range: {e}")
            return

        # Clear previous data
        for iid in self.report_tree.get_children():
            self.report_tree.delete(iid)
        for label in self.metrics_labels.values():
            label.config(text="N/A")

        all_vehicles = self.fleet_data_model.get_all_vehicles()
        all_trips = self.fleet_data_model.get_all_trips()
        all_maintenance_logs = self.fleet_data_model.get_all_maintenance_logs()
        all_fuel_logs = self.fleet_data_model.get_all_fuel_logs()

        filtered_vehicles = [v for v in all_vehicles if selected_vehicle_id == "All Vehicles" or v.vehicle_id == selected_vehicle_id]

        overall_total_operational_cost = 0.0
        overall_total_distance = 0.0
        overall_total_fuel_consumed = 0.0

        detailed_report_rows = []

        for vehicle in filtered_vehicles:
            vehicle_trips = [t for t in all_trips if t.vehicle_id == vehicle.vehicle_id and t.status == TripStatus.COMPLETED and 
                             t.end_time and start_date <= datetime.strptime(t.end_time.split("T")[0], "%Y-%m-%d").date() <= end_date]
            vehicle_maintenance = [ml for ml in all_maintenance_logs if ml.vehicle_id == vehicle.vehicle_id and 
                                   start_date <= datetime.strptime(ml.date, "%Y-%m-%d").date() <= end_date]
            vehicle_fuel_logs = [fl for fl in all_fuel_logs if fl.vehicle_id == vehicle.vehicle_id and 
                                 start_date <= datetime.strptime(fl.date, "%Y-%m-%d").date() <= end_date]

            total_distance_km = sum((t.end_odometer - t.start_odometer) for t in vehicle_trips if t.end_odometer is not None and t.start_odometer is not None)
            total_fuel_consumed_L = sum(fl.liters for fl in vehicle_fuel_logs)
            total_fuel_cost = sum(fl.cost for fl in vehicle_fuel_logs)
            total_maintenance_cost = sum(ml.cost for ml in vehicle_maintenance)
            
            # Simple placeholder for revenue per trip
            # A more complex system would involve actual revenue tracking
            average_revenue_per_trip = 150.0 # Example revenue
            total_revenue = len(vehicle_trips) * average_revenue_per_trip

            total_operational_cost = total_fuel_cost + total_maintenance_cost
            
            fuel_efficiency = (total_distance_km / total_fuel_consumed_L) if total_fuel_consumed_L > 0 else 0.0
            
            # Vehicle ROI calculation
            # Protect against division by zero if acquisition_cost is 0
            if vehicle.acquisition_cost > 0:
                vehicle_roi = ((total_revenue - total_operational_cost) / vehicle.acquisition_cost) * 100
            else:
                vehicle_roi = 0.0 # Cannot calculate ROI if acquisition cost is zero

            # Update overall totals
            overall_total_operational_cost += total_operational_cost
            overall_total_distance += total_distance_km
            overall_total_fuel_consumed += total_fuel_consumed_L
            
            detailed_report_rows.append((
                vehicle.vehicle_id,
                f"{total_distance_km:.2f}",
                f"{total_fuel_consumed_L:.2f}",
                f"${total_fuel_cost:.2f}", # Formatted as currency
                f"${total_maintenance_cost:.2f}", # Formatted as currency
                f"${total_operational_cost:.2f}", # Formatted as currency
                f"{fuel_efficiency:.2f}",
                f"{vehicle_roi:.2f}%"
            ))

        # Update summary metrics labels
        self.metrics_labels["Total Operational Cost"].config(text=f"${overall_total_operational_cost:.2f}")
        self.metrics_labels["Total Distance Covered"].config(text=f"{overall_total_distance:.2f} km")
        self.metrics_labels["Total Fuel Consumed"].config(text=f"{overall_total_fuel_consumed:.2f} L")
        
        overall_fuel_efficiency = (overall_total_distance / overall_total_fuel_consumed) if overall_total_fuel_consumed > 0 else 0.0
        self.metrics_labels["Fuel Efficiency (km/L)"].config(text=f"{overall_fuel_efficiency:.2f}")

        # Overall ROI calculation for "All Vehicles" view
        # Ensure all acquisition costs are summed for overall ROI
        if selected_vehicle_id == "All Vehicles" and len(filtered_vehicles) > 0:
            total_acq_cost = sum(v.acquisition_cost for v in filtered_vehicles)
            
            if total_acq_cost > 0:
                # Recalculate overall revenue, operational cost across all filtered vehicles
                all_filtered_trips_for_overall_roi = [t for v in filtered_vehicles for t in all_trips if t.vehicle_id == v.vehicle_id and t.status == TripStatus.COMPLETED and 
                                  t.end_time and start_date <= datetime.strptime(t.end_time.split("T")[0], "%Y-%m-%d").date() <= end_date]
                all_filtered_maintenance_for_overall_roi = [ml for v in filtered_vehicles for ml in all_maintenance_logs if ml.vehicle_id == v.vehicle_id and 
                                            start_date <= datetime.strptime(ml.date, "%Y-%m-%d").date() <= end_date]
                all_filtered_fuel_logs_for_overall_roi = [fl for v in filtered_vehicles for fl in all_fuel_logs if fl.vehicle_id == v.vehicle_id and 
                                          start_date <= datetime.strptime(fl.date, "%Y-%m-%d").date() <= end_date]
                
                overall_total_revenue_calc = len(all_filtered_trips_for_overall_roi) * average_revenue_per_trip
                overall_total_maintenance_cost_calc = sum(ml.cost for ml in all_filtered_maintenance_for_overall_roi)
                overall_total_fuel_cost_calc = sum(fl.cost for fl in all_filtered_fuel_logs_for_overall_roi)
                overall_total_operational_cost_calc = overall_total_maintenance_cost_calc + overall_total_fuel_cost_calc

                overall_roi = ((overall_total_revenue_calc - overall_total_operational_cost_calc) / total_acq_cost) * 100
                self.metrics_labels["Vehicle ROI"].config(text=f"{overall_roi:.2f}%")
            else:
                self.metrics_labels["Vehicle ROI"].config(text="0.00%") # No acquisition cost
        else: # For single vehicle selection, use its individual ROI
            if detailed_report_rows:
                # Assuming ROI is the last element in the detailed row tuple (index 7)
                self.metrics_labels["Vehicle ROI"].config(text=detailed_report_rows[0][7])
            else:
                self.metrics_labels["Vehicle ROI"].config(text="0.00%")


        # Populate detailed report table
        for row in detailed_report_rows:
            self.report_tree.insert("", "end", values=row)

    def export_report_csv(self):
        if not has_permission(self.user_role, ANALYTICS_PERMISSIONS["export"]):
            messagebox.showerror("Permission Denied", "You do not have permission to export reports.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                               filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                
                # Write summary metrics
                writer.writerow(["Metric", "Value"])
                for metric, label_widget in self.metrics_labels.items():
                    writer.writerow([metric, label_widget.cget("text")])
                writer.writerow([]) # Blank line

                # Write detailed report headers
                writer.writerow(self.report_tree["columns"])
                # Write detailed report data
                for item_id in self.report_tree.get_children():
                    writer.writerow(self.report_tree.item(item_id)["values"])
            
            messagebox.showinfo("Export Successful", f"Report exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {e}")
