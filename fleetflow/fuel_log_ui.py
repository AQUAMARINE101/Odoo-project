import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from fleetflow.theme import DARK_THEME, LIGHT_THEME, FONT_FAMILY
from fleetflow.permissions import has_permission, FUEL_LOG_PERMISSIONS # Correctly import FUEL_LOG_PERMISSIONS
from fleetflow.fleet_data_model import FleetDataModel, FuelLog # Import FuelLog
from fleetflow.ui_components import BasePage # Import BasePage

class FuelLogUI(BasePage):
    def __init__(self, master, controller, fleet_data_model, user_role="Guest"):
        super().__init__(master, controller, fleet_data_model, user_role)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_ui()
        self.refresh_vehicle_dropdown()
        self.refresh_table()
        self.controller.subscribe("fuel_log_updated", self.refresh_table) # Subscribe to fuel log updates
        self.controller.subscribe("vehicle_updated", self.refresh_vehicle_dropdown) # Vehicle updates affect dropdown
        self.controller.subscribe("maintenance_updated", self.update_operational_cost) # Also update on maintenance changes
        self.vehicle_combo.bind("<<ComboboxSelected>>", self.update_operational_cost) # Update cost when vehicle changes

    # --------------------------------------------
    # UI Construction
    # --------------------------------------------
    def build_ui(self):
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0) # Row for back button

        # Header
        self.create_label(self,
                 text="⛽ Fuel Logging",
                 font_size=18, font_weight="bold").grid(row=0, column=0,
                               columnspan=2, sticky="ew", pady=12, padx=10)

        self.build_form(self)
        self.build_table(self)

        # Back button
        self.create_back_button(self).grid(row=2, column=0, columnspan=2, pady=10)

    # --------------------------------------------
    # Form Panel
    # --------------------------------------------
    def build_form(self, parent_frame):
        form = ttk.Frame(parent_frame, style='FuelLogCard.TFrame')
        form.grid(row=1, column=0, sticky="ns", padx=20, pady=20)
        form.grid_columnconfigure(1, weight=1)

        row_idx = 0

        self.create_label(form, text="Vehicle ID", style='FuelLogCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.vehicle_var = tk.StringVar()
        self.vehicle_combo = ttk.Combobox(
            form,
            textvariable=self.vehicle_var,
            state="readonly" if has_permission(self.user_role, FUEL_LOG_PERMISSIONS["add"]) else "disabled"
        )
        self.vehicle_combo.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        self.create_label(form, text="Liters", style='FuelLogCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.liters_entry = ttk.Entry(form,
                                    state="normal" if has_permission(self.user_role, FUEL_LOG_PERMISSIONS["add"]) else "disabled")
        self.liters_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        self.create_label(form, text="Cost ($)", style='FuelLogCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.cost_entry = ttk.Entry(form,
                                    state="normal" if has_permission(self.user_role, FUEL_LOG_PERMISSIONS["add"]) else "disabled")
        self.cost_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        self.create_label(form, text="Date (YYYY-MM-DD)", style='FuelLogCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.date_entry = ttk.Entry(form,
                                    state="normal" if has_permission(self.user_role, FUEL_LOG_PERMISSIONS["add"]) else "disabled")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Default to today
        self.date_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        self.create_button(form,
                  text="Add Fuel Log",
                  command=self.safe_add_fuel_log,
                  style="Accent.TButton",
                  state="normal" if has_permission(self.user_role, FUEL_LOG_PERMISSIONS["add"]) else "disabled").grid(row=row_idx, column=0, columnspan=2, pady=15, sticky="ew")
        row_idx += 1
        
        # Operational Cost Display
        self.total_op_cost_label = self.create_label(form, text="Total Operational Cost: $0.00",
                                             font_size=12, font_weight="bold",
                                             style='FuelLogCard.TLabel')
        self.total_op_cost_label.grid(row=row_idx, column=0, columnspan=2, pady=(20, 5))

    # --------------------------------------------
    # Table Panel
    # --------------------------------------------
    def build_table(self, parent_frame):
        table_frame = ttk.Frame(parent_frame, style='FuelLog.TFrame')
        table_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        columns = ("ID", "Vehicle", "Liters", "Cost", "Date")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="FuelLogTreeview"
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        
        self.tree.column("ID", width=70) # Truncate ID for better fit
        self.tree.column("Vehicle", width=90)
        self.tree.column("Liters", width=80)
        self.tree.column("Cost", width=80)
        self.tree.column("Date", width=90)

        self.tree.pack(fill="both", expand=True)

    # --------------------------------------------
    # Safe Wrappers
    # --------------------------------------------
    def safe_add_fuel_log(self):
        try:
            self.add_fuel_log()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add fuel log: {e}")

    # --------------------------------------------
    # Business Logic Integration
    # --------------------------------------------
    def add_fuel_log(self):
        vehicle_id = self.vehicle_var.get().strip()
        liters_input = self.liters_entry.get().strip()
        cost_input = self.cost_entry.get().strip()
        date_input = self.date_entry.get().strip()

        if not vehicle_id or not liters_input or not cost_input or not date_input:
            messagebox.showwarning("Validation", "All fields required.")
            return

        try:
            liters = float(liters_input)
            if liters <= 0:
                raise ValueError("Liters must be a positive number.")
            cost = float(cost_input)
            if cost <= 0:
                raise ValueError("Cost must be a positive number.")
            datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError as e:
            messagebox.showerror("Validation", f"Invalid input: {e}")
            return

        try:
            new_log = FuelLog(vehicle_id, liters, cost, date=date_input)
            self.fleet_data_model.add_fuel_log(new_log)

            self.refresh_table()
            self.clear_form()
            self.controller.publish("fuel_log_updated") # Notify dashboard and other listeners
            # Consider publishing vehicle_updated if fuel log implies any change to vehicle status (unlikely directly)

            messagebox.showinfo("Success", f"Fuel log added for {vehicle_id}.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def update_operational_cost(self, *args):
        selected_vehicle_id = self.vehicle_var.get()
        if not selected_vehicle_id:
            self.total_op_cost_label.config(text="Total Operational Cost: $0.00")
            return

        total_cost = 0.0
        
        # Sum fuel costs for the selected vehicle
        for log in self.fleet_data_model.get_all_fuel_logs():
            if log.vehicle_id == selected_vehicle_id:
                total_cost += log.cost
        
        # Sum maintenance costs for the selected vehicle
        for log in self.fleet_data_model.get_all_maintenance_logs():
            if log.vehicle_id == selected_vehicle_id:
                total_cost += log.cost

        self.total_op_cost_label.config(text=f"Total Operational Cost: ${total_cost:.2f}")

    # --------------------------------------------
    # Helpers
    # --------------------------------------------
    def refresh_vehicle_dropdown(self, *args):
        # Get active vehicles from FleetDataModel (not out of service)
        active_vehicles = [v.vehicle_id for v in self.fleet_data_model.get_all_vehicles() if not v.out_of_service]
        self.vehicle_combo["values"] = active_vehicles
        if active_vehicles:
            self.vehicle_combo.current(0)
            self.update_operational_cost() # Update cost for the initially selected vehicle
        else:
            self.vehicle_var.set("")
            self.total_op_cost_label.config(text="Total Operational Cost: $0.00") # Reset if no vehicles

    def refresh_table(self, *args):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for log in self.fleet_data_model.get_all_fuel_logs():
            self.tree.insert("", "end",
                             values=(log.log_id[:5] + "...", # Truncate ID for display
                                     log.vehicle_id, log.liters, log.cost, log.date))

    def clear_form(self):
        self.liters_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Reset to today's date