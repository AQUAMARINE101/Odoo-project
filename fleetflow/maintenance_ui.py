import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from fleetflow.theme import DARK_THEME, LIGHT_THEME, FONT_FAMILY
from fleetflow.fleet_data_model import FleetDataModel, MaintenanceLog # Import FleetDataModel and MaintenanceLog
from fleetflow.permissions import has_permission, MAINTENANCE_PERMISSIONS # Import permissions
from fleetflow.ui_components import BasePage # Import BasePage

class MaintenancePage(BasePage): # Inherit from BasePage
    def __init__(self, master, controller, fleet_data_model, user_role="Guest"):
        super().__init__(master, controller, fleet_data_model, user_role) # Call BasePage.__init__

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_ui()
        self.refresh_vehicle_dropdown()
        self.refresh_table()
        self.controller.subscribe("maintenance_updated", self.refresh_table) # Subscribe to updates
        self.controller.subscribe("vehicle_updated", self.refresh_vehicle_dropdown) # Vehicle updates affect dropdown

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
                 text="🔧 Maintenance & Service Logs",
                 font_size=18, font_weight="bold",
                 style="TLabel").grid(row=0, column=0,
                               columnspan=2, sticky="ew", pady=12, padx=10)

        self.build_form(self)
        self.build_table(self)

        # Back button
        self.create_back_button(self).grid(row=2, column=0, columnspan=2, pady=10)


    # --------------------------------------------
    # Form Panel
    # --------------------------------------------
    def build_form(self, parent_frame):
        form = ttk.Frame(parent_frame, style='MaintenanceCard.TFrame')
        form.grid(row=1, column=0, sticky="ns", padx=20, pady=20)
        form.grid_columnconfigure(1, weight=1)

        row_idx = 0

        self.create_label(form, text="Vehicle ID", style='MaintenanceCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.vehicle_var = tk.StringVar()
        self.vehicle_combo = ttk.Combobox(
            form,
            textvariable=self.vehicle_var,
            state="readonly" if has_permission(self.user_role, MAINTENANCE_PERMISSIONS["add"]) else "disabled"
        )
        self.vehicle_combo.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        self.create_label(form, text="Service Description", style='MaintenanceCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.desc_entry = ttk.Entry(form,
                                    state="normal" if has_permission(self.user_role, MAINTENANCE_PERMISSIONS["add"]) else "disabled")
        self.desc_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        self.create_label(form, text="Cost ($)", style='MaintenanceCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.cost_entry = ttk.Entry(form,
                                    state="normal" if has_permission(self.user_role, MAINTENANCE_PERMISSIONS["add"]) else "disabled")
        self.cost_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        self.create_label(form, text="Date (YYYY-MM-DD)", style='MaintenanceCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.date_entry = ttk.Entry(form,
                                    state="normal" if has_permission(self.user_role, MAINTENANCE_PERMISSIONS["add"]) else "disabled")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Default to today
        self.date_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        self.add_btn = self.create_button(form,
                  text="Add Service",
                  command=self.safe_add_service,
                  style="Accent.TButton",
                  state="normal" if has_permission(self.user_role, MAINTENANCE_PERMISSIONS["add"]) else "disabled")
        self.add_btn.grid(row=row_idx, column=0, columnspan=2, pady=15, sticky="ew")
        row_idx += 1

        self.complete_btn = self.create_button(form,
                  text="Complete Selected",
                  command=self.safe_complete_service,
                  style="Info.TButton",
                  state="normal" if has_permission(self.user_role, MAINTENANCE_PERMISSIONS["update"]) else "disabled")
        self.complete_btn.grid(row=row_idx, column=0, columnspan=2, sticky="ew")

    # --------------------------------------------
    # Table Panel
    # --------------------------------------------
    def build_table(self, parent_frame):
        table_frame = ttk.Frame(parent_frame, style='Maintenance.TFrame')
        table_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        columns = ("ID", "Vehicle", "Description", "Cost", "Date", "Status")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="MaintenanceTreeview"
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        
        self.tree.column("ID", width=70) # Truncate ID for better fit
        self.tree.column("Vehicle", width=90)
        self.tree.column("Description", width=200)
        self.tree.column("Cost", width=70)
        self.tree.column("Date", width=90)
        self.tree.column("Status", width=80)

        self.tree.pack(fill="both", expand=True)

    # --------------------------------------------
    # Safe Wrappers
    # --------------------------------------------
    def safe_add_service(self):
        try:
            self.add_service()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add service: {e}")

    def safe_complete_service(self):
        try:
            self.complete_service()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete service: {e}")

    # --------------------------------------------
    # Business Logic Integration
    # --------------------------------------------
    def add_service(self):
        vehicle_id = self.vehicle_var.get().strip()
        description = self.desc_entry.get().strip()
        cost_input = self.cost_entry.get().strip()
        date_input = self.date_entry.get().strip() # Get date input

        if not vehicle_id or not description or not cost_input or not date_input:
            messagebox.showwarning("Validation", "All fields required.")
            return

        try:
            cost = float(cost_input)
            if cost <= 0:
                raise ValueError("Cost must be a positive number.")
            # Validate date format
            datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError as e:
            messagebox.showerror("Validation", f"Invalid input: {e}")
            return

        try:
            # Use FleetDataModel to add maintenance log
            new_log = MaintenanceLog(vehicle_id, description, cost, date=date_input) # Pass date
            self.fleet_data_model.add_maintenance_log(new_log)

            self.refresh_table()
            self.clear_form()
            self.controller.publish("maintenance_updated") # Notify dashboard
            self.controller.publish("vehicle_updated") # Notify vehicle registry for status change

            messagebox.showinfo("Success",
                                f"{vehicle_id} status updated for service.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add service: {e}")


    def complete_service(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a log first.")
            return

        item = self.tree.item(selected[0])
        log_id = item["values"][0] # Assuming ID is the first column
        status = item["values"][5] # Assuming Status is the sixth column

        if status == "Completed":
            messagebox.showinfo("Info", "Service already completed.")
            return

        try:
            # Use FleetDataModel to update maintenance log status
            self.fleet_data_model.update_maintenance_log_status(log_id, "Completed")

            self.refresh_table()
            self.controller.publish("maintenance_updated") # Notify dashboard
            self.controller.publish("vehicle_updated") # Notify vehicle registry for status change

            messagebox.showinfo("Completed",
                                f"Service for {item['values'][1]} is now Completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete service: {e}")


    # --------------------------------------------
    # Helpers
    # --------------------------------------------
    def refresh_vehicle_dropdown(self, *args):
        # Get available vehicles from FleetDataModel that are not out of service
        active_vehicles = [v.vehicle_id for v in self.fleet_data_model.get_all_vehicles() if not v.out_of_service]
        self.vehicle_combo["values"] = active_vehicles
        if active_vehicles:
            self.vehicle_combo.current(0)
        else:
            self.vehicle_combo.set("")

    def refresh_table(self, *args):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for log in self.fleet_data_model.get_all_maintenance_logs():
            tag = log.status + ".MaintenanceTreeview" # Tag for styling
            self.tree.insert("", "end",
                             values=(log.log_id[:5] + "...", # Truncate ID for display
                                     log.vehicle_id,
                                     log.description,
                                     log.cost,
                                     log.date,
                                     log.status),
                             tags=(tag,)) # Apply status tag for styling

    def clear_form(self):
        self.desc_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END) # Clear date entry
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Reset to today's date

