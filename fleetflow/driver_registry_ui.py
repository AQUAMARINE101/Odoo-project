import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime # Import datetime
from fleetflow.theme import DARK_THEME, LIGHT_THEME, FONT_FAMILY
from fleetflow.permissions import has_permission, DRIVER_REGISTRY_PERMISSIONS
from fleetflow.fleet_data_model import FleetDataModel, Driver, DriverStatus # Import DriverStatus
from fleetflow.ui_components import BasePage # Import BasePage

class DriverRegistryUI(BasePage): # Inherit from BasePage
    def __init__(self, master, controller, fleet_data_model, user_role="Guest"):
        super().__init__(master, controller, fleet_data_model, user_role) # Call BasePage.__init__
        
        self.build_ui()
        self.refresh_table()
        # Subscribe to driver updates to refresh the table if changes occur elsewhere
        self.subscribe("driver_updated", self.refresh_table)

    # ---------------- UI LAYOUT ----------------

    def build_ui(self):
        self.pack(fill="both", expand=True)

        # Top Bar
        top = ttk.Frame(self, style='DriverRegistry.TFrame', height=50)
        top.pack(fill="x", padx=10, pady=10)

        self.create_label(top, text="👨‍✈️ Driver Registry Dashboard",
                 font_size=16, font_weight="bold").pack(side="left", padx=15)
        self.create_back_button(top).pack(side="right", padx=10, pady=10)

        # Content Frame: Form + Table
        content_frame = ttk.Frame(self, style='DriverRegistry.TFrame')
        content_frame.pack(pady=10, fill="both", expand=True)
        content_frame.grid_columnconfigure(0, weight=1) # Form column
        content_frame.grid_columnconfigure(1, weight=2) # Table column
        content_frame.grid_rowconfigure(0, weight=1)

        # Form Section
        form_section = ttk.Frame(content_frame, style='DriverCard.TFrame')
        form_section.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        form_section.grid_columnconfigure(1, weight=1)

        self.create_label(form_section, text="Driver Details",
                 font_size=14, font_weight="bold",
                 style='DriverCard.TLabel').grid(row=0, column=0, columnspan=2, pady=(0,10))

        row_idx = 1
        self.entries = {}
        
        form_fields = ["ID", "Name", "License Expiry", "Safety Score"]
        for label_text in form_fields:
            self.create_label(form_section, text=label_text, style='DriverCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(2,0), sticky="w")
            e = ttk.Entry(form_section, width=25)
            e.grid(row=row_idx, column=1, padx=5, pady=(0,5), sticky="ew")
            self.entries[label_text] = e
            
            if (not has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["add"]) and 
                not has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["update"])):
                e.config(state="disabled")
            row_idx += 1
        
        self.create_label(form_section, text="Status", style='DriverCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(2,0), sticky="w")
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(
            form_section,
            textvariable=self.status_var,
            values=[status.value for status in DriverStatus],
            state="readonly" if has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["update"]) else "disabled",
            width=23
        )
        status_combo.grid(row=row_idx, column=1, padx=5, pady=(0,5), sticky="ew")
        self.entries["Status"] = status_combo
        self.status_var.set(DriverStatus.OFF_DUTY.value)
        row_idx += 1

        # Buttons
        btns = ttk.Frame(form_section, style='DriverCard.TFrame')
        btns.grid(row=row_idx, column=0, columnspan=2, pady=10, sticky="ew")
        btns.grid_columnconfigure((0, 1), weight=1)

        self.create_button(btns, text="Add", command=self.add_driver, style="Accent.TButton",
                           state="normal" if has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["add"]) else "disabled").grid(row=0, column=0, padx=2, pady=5, sticky="ew")
        self.create_button(btns, text="Update", command=self.update_driver, style="Primary.TButton",
                           state="normal" if has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["update"]) else "disabled").grid(row=0, column=1, padx=2, pady=5, sticky="ew")
        self.create_button(btns, text="Delete", command=self.delete_driver, style="Danger.TButton",
                           state="normal" if has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["delete"]) else "disabled").grid(row=1, column=0, columnspan=2, padx=2, pady=5, sticky="ew")
        
        self.create_button(btns, text="Toggle Status", command=self.toggle_status, style="Warning.TButton",
                           state="normal" if has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["toggle_status"]) else "disabled").grid(row=2, column=0, columnspan=2, padx=2, pady=5, sticky="ew")
        row_idx += 1


        # Performance Metrics Section
        performance_section = ttk.Frame(form_section, style='DriverCard.TFrame')
        performance_section.grid(row=row_idx, column=0, columnspan=2, pady=15, sticky="ew")
        performance_section.grid_columnconfigure(0, weight=1)

        self.create_label(performance_section, text="Performance Metrics",
                 font_size=12, font_weight="bold",
                 style='DriverCard.TLabel').grid(row=0, column=0, pady=(0,5), sticky="w")
        
        self.trip_completion_rate_label = self.create_label(performance_section,
                                                            text="Trip Completion Rate: N/A",
                                                            style='DriverCard.TLabel')
        self.trip_completion_rate_label.grid(row=1, column=0, sticky="w")

        # Table Section
        table_section = ttk.Frame(content_frame, style='DriverRegistry.TFrame')
        table_section.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        table_section.grid_rowconfigure(1, weight=1)
        table_section.grid_columnconfigure(0, weight=1)

        self.create_label(table_section, text="Driver List",
                 font_size=14, font_weight="bold").pack(pady=(0,10))

        columns = ("ID", "Name", "License Expiry", "Safety Score", "Status") # Updated columns
        self.tree = ttk.Treeview(table_section, columns=columns, show="headings", style="DriverTreeview")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        
        self.tree.column("ID", width=70)
        self.tree.column("Name", width=100)
        self.tree.column("License Expiry", width=100)
        self.tree.column("Safety Score", width=80)
        self.tree.column("Status", width=90)


        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)


    # ---------------- CRUD OPERATIONS (No change to logic, just UI calls) ----------------
    def add_driver(self):
        if not has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["add"]):
            messagebox.showerror("Permission Denied", "You do not have permission to add drivers.")
            return

        driver_id = self.entries["ID"].get().strip()
        name = self.entries["Name"].get().strip()
        license_expiry = self.entries["License Expiry"].get().strip()
        safety_score_str = self.entries["Safety Score"].get().strip()
        status_value = self.status_var.get()

        if not driver_id or not name or not license_expiry or not safety_score_str or not status_value:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            safety_score = int(safety_score_str)
            if not (0 <= safety_score <= 100):
                raise ValueError("Safety Score must be between 0 and 100.")
            status = DriverStatus(status_value) # Convert string to Enum
            # Validate license expiry date format
            if license_expiry != "N/A":
                datetime.strptime(license_expiry, "%Y-%m-%d")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return

        try:
            new_driver = Driver(driver_id=driver_id, name=name, license_expiry=license_expiry, status=status, safety_score=safety_score)
            self.fleet_data_model.add_driver(new_driver)
            messagebox.showinfo("Success", f"Driver {driver_id} added.")
            self.refresh_table()
            self.controller.publish("driver_updated")
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to add driver: {e}")

    def update_driver(self):
        if not has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["update"]):
            messagebox.showerror("Permission Denied", "You do not have permission to update drivers.")
            return

        driver_id = self.entries["ID"].get().strip()
        driver = self.fleet_data_model.get_driver(driver_id)
        if not driver:
            messagebox.showerror("Error", f"Driver {driver_id} not found.")
            return

        name = self.entries["Name"].get().strip()
        license_expiry = self.entries["License Expiry"].get().strip()
        safety_score_str = self.entries["Safety Score"].get().strip()
        status_value = self.status_var.get()

        if not name or not license_expiry or not safety_score_str or not status_value:
            messagebox.showerror("Error", "All fields are required for update.")
            return
        
        try:
            safety_score = int(safety_score_str)
            if not (0 <= safety_score <= 100):
                raise ValueError("Safety Score must be between 0 and 100.")
            status = DriverStatus(status_value) # Convert string to Enum
            # Validate license expiry date format
            if license_expiry != "N/A":
                datetime.strptime(license_expiry, "%Y-%m-%d")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return

        try:
            self.fleet_data_model.update_driver(driver_id, name=name, license_expiry=license_expiry, status=status, safety_score=safety_score)
            messagebox.showinfo("Success", f"Driver {driver_id} updated.")
            self.refresh_table()
            self.controller.publish("driver_updated")
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to update driver: {e}")

    def delete_driver(self):
        if not has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["delete"]):
            messagebox.showerror("Permission Denied", "You do not have permission to delete drivers.")
            return

        driver_id = self.entries["ID"].get().strip()
        if not self.fleet_data_model.get_driver(driver_id):
            messagebox.showerror("Error", f"Driver {driver_id} not found.")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete driver {driver_id}?"):
            try:
                self.fleet_data_model.delete_driver(driver_id)
                messagebox.showinfo("Success", f"Driver {driver_id} deleted.")
                self.refresh_table()
                self.controller.publish("driver_updated")
                self.clear_form()
            except ValueError as e:
                messagebox.showerror("Error", f"Failed to delete driver: {e}")

    def toggle_status(self):
        if not has_permission(self.user_role, DRIVER_REGISTRY_PERMISSIONS["toggle_status"]):
            messagebox.showerror("Permission Denied", "You do not have permission to toggle driver status.")
            return

        driver_id = self.entries["ID"].get().strip()
        driver = self.fleet_data_model.get_driver(driver_id)
        if not driver:
            messagebox.showerror("Error", f"Driver {driver_id} not found.")
            return
        
        try:
            # Cycle through DriverStatus: OFF_DUTY -> ON_DUTY -> SUSPENDED -> OFF_DUTY
            current_status_index = list(DriverStatus).index(driver.status)
            next_status_index = (current_status_index + 1) % len(list(DriverStatus))
            new_status = list(DriverStatus)[next_status_index]

            self.fleet_data_model.update_driver(driver_id, status=new_status)
            messagebox.showinfo("Success", f"Driver {driver_id} status toggled to {new_status.value}.")
            self.refresh_table()
            self.controller.publish("driver_updated")
            # Removed self.clear_form() from here
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to toggle driver status: {e}")

    # ---------------- TABLE ----------------

    def refresh_table(self, *args): # *args to accept event data if published
        for row in self.tree.get_children():
            self.tree.delete(row)

        current_date = datetime.now().date()

        for driver in self.fleet_data_model.get_all_drivers():
            tags = [driver.status.name + ".DriverTreeview"] # Apply status tag

            # Check for expired license
            if driver.license_expiry != "N/A":
                try:
                    expiry_date = datetime.strptime(driver.license_expiry, "%Y-%m-%d").date()
                    if expiry_date < current_date:
                        tags.append("expired_license.DriverTreeview") # Add expired license tag
                except ValueError:
                    # Handle invalid date format in stored data if necessary
                    pass

            self.tree.insert("", "end",
                             values=(driver.driver_id, driver.name, driver.license_expiry, driver.safety_score, driver.status.value),
                             tags=tuple(tags)) # Apply all tags

    def load_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        self.entries["ID"].delete(0, tk.END)
        self.entries["ID"].insert(0, values[0])
        self.entries["Name"].delete(0, tk.END)
        self.entries["Name"].insert(0, values[1])
        self.entries["License Expiry"].delete(0, tk.END)
        self.entries["License Expiry"].insert(0, values[2])
        self.entries["Safety Score"].delete(0, tk.END)
        self.entries["Safety Score"].insert(0, values[3])
        self.status_var.set(values[4]) # Set combobox based on status value

        # Update performance metrics for selected driver
        self.update_driver_performance_metrics(values[0])


    def clear_form(self):
        self.entries["ID"].delete(0, tk.END)
        self.entries["Name"].delete(0, tk.END)
        self.entries["License Expiry"].delete(0, tk.END)
        self.entries["Safety Score"].delete(0, tk.END)
        self.status_var.set(DriverStatus.OFF_DUTY.value) # Reset status to default
        self.trip_completion_rate_label.config(text="Trip Completion Rate: N/A") # Clear performance metric

    def update_driver_performance_metrics(self, driver_id):
        # Placeholder for actual calculation
        # This would ideally come from fleet_data_model after calculating based on trips
        trips = self.fleet_data_model.get_all_trips()
        driver_trips = [t for t in trips if t.driver_id == driver_id]
        
        total_trips = len(driver_trips)
        completed_trips = len([t for t in driver_trips if t.status == TripStatus.COMPLETED])

        if total_trips > 0:
            completion_rate = (completed_trips / total_trips) * 100
            self.trip_completion_rate_label.config(text=f"Trip Completion Rate: {completion_rate:.1f}%")
        else:
            self.trip_completion_rate_label.config(text="Trip Completion Rate: 0.0%")