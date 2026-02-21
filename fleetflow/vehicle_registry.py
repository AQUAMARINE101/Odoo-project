import tkinter as tk
from tkinter import ttk, messagebox
import math
from fleetflow.theme import DARK_THEME, LIGHT_THEME, FONT_FAMILY
from fleetflow.permissions import has_permission, VEHICLE_REGISTRY_PERMISSIONS
from fleetflow.fleet_data_model import FleetDataModel, Vehicle # Import FleetDataModel and Vehicle
from fleetflow.ui_components import BasePage # Import BasePage

class VehicleRegistryUI(BasePage): # Inherit from BasePage
    def __init__(self, master, controller, fleet_data_model, user_role="Guest"): # Accept master, controller, fleet_data_model, user_role
        super().__init__(master, controller, fleet_data_model, user_role) # Call BasePage.__init__

        self.build_ui()
        self.refresh_table()
        self.update_stats()
        # Subscribe to relevant events
        self.subscribe("vehicle_updated", self.refresh_table) # Subscribe to vehicle updates
        self.subscribe("vehicle_updated", self.update_stats) # Subscribe to vehicle updates to refresh stats


    # ---------------- UI LAYOUT ----------------

    def build_ui(self):
        self.pack(fill="both", expand=True)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top Bar (Header and Stats Button)
        top = ttk.Frame(self, style='VehicleRegistry.TFrame')
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        top.grid_columnconfigure(0, weight=1) # Title
        top.grid_columnconfigure(1, weight=0) # Stats button
        top.grid_columnconfigure(2, weight=0) # Back button

        self.create_label(top, text="🚘 Vehicle Registry Dashboard", font_size=16, font_weight="bold").grid(row=0, column=0, sticky="w")

        self.create_button(top, text="📊 Stats",
                  command=self.toggle_stats_panel,
                  style="Warning.TButton",
                  state="normal" if has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["view_stats"]) else "disabled").grid(row=0, column=1, padx=10, pady=10, sticky="e")

        self.create_back_button(top).grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # Content Area (Form, Buttons, Table)
        content_area = ttk.Frame(self, style='VehicleRegistry.TFrame')
        content_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_area.grid_columnconfigure(0, weight=1)
        content_area.grid_rowconfigure(2, weight=1)

        # Form
        form = ttk.Frame(content_area, style='VehicleRegistry.TFrame')
        form.grid(row=0, column=0, pady=5, sticky="ew")
        form.grid_columnconfigure((1, 3, 5, 7), weight=1)

        self.entries = {}
        labels_row1 = [("Plate", "Plate"), ("Model", "Model"), ("Capacity", "Capacity"), ("Odometer", "Odometer")]
        labels_row2 = [("Acquisition Cost", "Acquisition Cost"), ("Type", "Type"), ("Region", "Region")]

        for i, (label_text, entry_key) in enumerate(labels_row1):
            self.create_label(form, text=label_text).grid(row=0, column=i*2, padx=5, pady=2, sticky="w")
            e = ttk.Entry(form, width=18)
            e.grid(row=0, column=i*2+1, padx=5, pady=2, sticky="ew")
            self.entries[entry_key] = e
            if not has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["add"]) and \
               not has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["update"]):
                e.config(state="disabled")

        for i, (label_text, entry_key) in enumerate(labels_row2):
            self.create_label(form, text=label_text).grid(row=1, column=i*2, padx=5, pady=2, sticky="w")
            if entry_key in ["Type", "Region"]:
                combo_var = tk.StringVar(value="Select")
                combo = ttk.Combobox(form, textvariable=combo_var, state="readonly", width=16)
                if entry_key == "Type":
                    combo['values'] = ["Car", "Van", "Truck", "Bike"]
                elif entry_key == "Region":
                    combo['values'] = ["North", "South", "East", "West", "Central"]
                combo.grid(row=1, column=i*2+1, padx=5, pady=2, sticky="ew")
                self.entries[entry_key] = combo
                self.entries[entry_key + "_var"] = combo_var
            else:
                e = ttk.Entry(form, width=18)
                e.grid(row=1, column=i*2+1, padx=5, pady=2, sticky="ew")
                self.entries[entry_key] = e
            
            if not has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["add"]) and \
               not has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["update"]):
                self.entries[entry_key].config(state="disabled")

        # Buttons
        btns = ttk.Frame(content_area, style='VehicleRegistry.TFrame')
        btns.grid(row=1, column=0, pady=5, sticky="ew")
        btns.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.create_button(btns, text="Add", command=self.add_vehicle, style="Accent.TButton",
                           state="normal" if has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["add"]) else "disabled").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.create_button(btns, text="Update", command=self.update_vehicle, style="Primary.TButton",
                           state="normal" if has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["update"]) else "disabled").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.create_button(btns, text="Delete", command=self.delete_vehicle, style="Danger.TButton",
                           state="normal" if has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["delete"]) else "disabled").grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.create_button(btns, text="Toggle Status", command=self.toggle_status, style="Warning.TButton",
                           state="normal" if has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["toggle_status"]) else "disabled").grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Table
        columns = ("Plate", "Model", "Capacity", "Odometer", "Type", "Region", "Status", "Acquisition Cost")
        self.tree = ttk.Treeview(content_area, columns=columns, show="headings", height=14, style="Treeview")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")
        
        self.tree.column("Plate", width=90)
        self.tree.column("Model", width=90)
        self.tree.column("Acquisition Cost", width=100)

        self.tree.grid(row=2, column=0, pady=15, padx=10, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)

        # Stats Panel
        self.stats_panel = ttk.Frame(self, style='KpiCard.TFrame', width=260)
        self.stats_panel.grid(row=1, column=1, sticky="ns", padx=(0,10), pady=(10,10))
        self.grid_columnconfigure(1, weight=0)
        self.stats_panel_visible = False
        self.stats_panel.grid_remove()

    # ---------------- CRUD OPERATIONS ----------------

    def add_vehicle(self):
        if not has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["add"]):
            messagebox.showerror("Permission Denied", "You do not have permission to add vehicles.")
            return

        plate = self.entries["Plate"].get().upper()
        model = self.entries["Model"].get()
        capacity_str = self.entries["Capacity"].get()
        odo_str = self.entries["Odometer"].get()
        acq_cost_str = self.entries["Acquisition Cost"].get() # Get acquisition cost

        # Added Type and Region
        vehicle_type = self.entries["Type_var"].get() if "Type_var" in self.entries else self.entries["Type"].get()
        region = self.entries["Region_var"].get() if "Region_var" in self.entries else self.entries["Region"].get()

        if not plate or not model or not capacity_str or not odo_str or not acq_cost_str or not vehicle_type or not region:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            capacity = float(capacity_str)
            odometer = int(odo_str)
            acquisition_cost = float(acq_cost_str)
            if capacity <= 0 or odometer < 0 or acquisition_cost < 0:
                raise ValueError("Capacity must be positive, Odometer and Acquisition Cost non-negative.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return

        try:
            new_vehicle = Vehicle(vehicle_id=plate, name=model, max_capacity=capacity, odometer=odometer, acquisition_cost=acquisition_cost, vehicle_type=vehicle_type, region=region)
            self.fleet_data_model.add_vehicle(new_vehicle)
            messagebox.showinfo("Success", f"Vehicle {plate} added.")
            self.refresh_table()
            self.update_stats()
            self.controller.publish("vehicle_updated") # Notify other modules
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to add vehicle: {e}")

    def update_vehicle(self):
        if not has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["update"]):
            messagebox.showerror("Permission Denied", "You do not have permission to update vehicles.")
            return

        plate = self.entries["Plate"].get().upper()
        vehicle = self.fleet_data_model.get_vehicle(plate)
        if not vehicle:
            messagebox.showerror("Error", f"Vehicle {plate} not found.")
            return

        model = self.entries["Model"].get()
        capacity_str = self.entries["Capacity"].get()
        odo_str = self.entries["Odometer"].get()
        acq_cost_str = self.entries["Acquisition Cost"].get() # Get acquisition cost

        # Added Type and Region
        vehicle_type = self.entries["Type_var"].get() if "Type_var" in self.entries else self.entries["Type"].get()
        region = self.entries["Region_var"].get() if "Region_var" in self.entries else self.entries["Region"].get()

        if not model or not capacity_str or not odo_str or not acq_cost_str or not vehicle_type or not region:
            messagebox.showerror("Error", "All fields are required for update.")
            return
        
        try:
            capacity = float(capacity_str)
            odometer = int(odo_str)
            acquisition_cost = float(acq_cost_str)
            if capacity <= 0 or odometer < 0 or acquisition_cost < 0:
                raise ValueError("Capacity must be positive, Odometer and Acquisition Cost non-negative.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return

        try:
            self.fleet_data_model.update_vehicle(plate, name=model, max_capacity=capacity, odometer=odometer, acquisition_cost=acquisition_cost, vehicle_type=vehicle_type, region=region)
            messagebox.showinfo("Success", f"Vehicle {plate} updated.")
            self.refresh_table()
            self.update_stats()
            self.controller.publish("vehicle_updated") # Notify other modules
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to update vehicle: {e}")

    def delete_vehicle(self):
        if not has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["delete"]):
            messagebox.showerror("Permission Denied", "You do not have permission to delete vehicles.")
            return

        plate = self.entries["Plate"].get().upper()
        if not self.fleet_data_model.get_vehicle(plate):
            messagebox.showerror("Error", f"Vehicle {plate} not found.")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete vehicle {plate}?"):
            try:
                self.fleet_data_model.delete_vehicle(plate)
                messagebox.showinfo("Success", f"Vehicle {plate} deleted.")
                self.refresh_table()
                self.update_stats()
                self.controller.publish("vehicle_updated") # Notify other modules
            except ValueError as e:
                messagebox.showerror("Error", f"Failed to delete vehicle: {e}")

    def toggle_status(self):
        if not has_permission(self.user_role, VEHICLE_REGISTRY_PERMISSIONS["toggle_status"]):
            messagebox.showerror("Permission Denied", "You do not have permission to toggle vehicle status.")
            return

        plate = self.entries["Plate"].get().upper()
        vehicle = self.fleet_data_model.get_vehicle(plate)
        if not vehicle:
            messagebox.showerror("Error", f"Vehicle {plate} not found.")
            return
        
        try:
            new_status = not vehicle.out_of_service
            self.fleet_data_model.update_vehicle(plate, out_of_service=new_status, available=not new_status)
            messagebox.showinfo("Success", f"Vehicle {plate} status toggled to {'Out of Service' if new_status else 'Active'}.")
            self.refresh_table()
            self.update_stats()
            self.controller.publish("vehicle_updated") # Notify other modules
        except ValueError as e:
            messagebox.showerror("Error", f"Failed to toggle vehicle status: {e}")

    # ---------------- TABLE ----------------

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for vehicle in self.fleet_data_model.get_all_vehicles():
            status = "Out of Service" if vehicle.out_of_service else "Active"
            tag = "out_of_service" if vehicle.out_of_service else "" # Apply tag for styling
            self.tree.insert("", "end",
                             values=(vehicle.vehicle_id, vehicle.name, vehicle.max_capacity,
                                     vehicle.odometer, vehicle.vehicle_type, vehicle.region, status, vehicle.acquisition_cost),
                             tags=(tag,))

    def load_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        # Exclude the "Status" column when loading into entries, as it's derived.
        # Order of values in tree: (Plate, Model, Capacity, Odometer, Type, Region, Status, Acquisition Cost)
        # Order of entry_keys: (Plate, Model, Capacity, Odometer, Acquisition Cost, Type, Region)
        
        # Manually map values to entries to avoid complex index logic
        self.entries["Plate"].delete(0, tk.END); self.entries["Plate"].insert(0, values[0])
        self.entries["Model"].delete(0, tk.END); self.entries["Model"].insert(0, values[1])
        self.entries["Capacity"].delete(0, tk.END); self.entries["Capacity"].insert(0, values[2])
        self.entries["Odometer"].delete(0, tk.END); self.entries["Odometer"].insert(0, values[3])
        
        # Handle Comboboxes (Type, Region)
        if "Type_var" in self.entries:
            self.entries["Type_var"].set(values[4]) # vehicle.vehicle_type
        else: # Fallback for entry if not combobox
            self.entries["Type"].delete(0, tk.END); self.entries["Type"].insert(0, values[4])
        
        if "Region_var" in self.entries:
            self.entries["Region_var"].set(values[5]) # vehicle.region
        else: # Fallback for entry if not combobox
            self.entries["Region"].delete(0, tk.END); self.entries["Region"].insert(0, values[5])

        self.entries["Acquisition Cost"].delete(0, tk.END); self.entries["Acquisition Cost"].insert(0, values[7]) # vehicle.acquisition_cost

    # ---------------- STATS & PIE CHART ----------------

    def update_stats(self):
        all_vehicles = self.fleet_data_model.get_all_vehicles()
        self.active = sum(1 for v in all_vehicles if not v.out_of_service)
        self.out = sum(1 for v in all_vehicles if v.out_of_service)

    def draw_pie_chart(self):
        for w in self.stats_panel.winfo_children():
            w.destroy()

        self.create_label(self.stats_panel, text="📊 Fleet Statistics",
                          font_size=14, font_weight="bold",
                          bg=DARK_THEME["card_bg"], fg=DARK_THEME["card_fg"]).pack(pady=15) # Changed fg

        self.create_label(self.stats_panel, text=f"Active Vehicles: {self.active}",
                          bg=DARK_THEME["card_bg"], fg=DARK_THEME["card_fg"]).pack() # Changed fg
        self.create_label(self.stats_panel, text=f"Out of Service: {self.out}",
                          bg=DARK_THEME["card_bg"], fg=DARK_THEME["card_fg"]).pack() # Changed fg

        canvas = tk.Canvas(self.stats_panel, width=200, height=200, bg=DARK_THEME["card_bg"], bd=0, highlightthickness=0) # Added highlightthickness
        canvas.pack(pady=20)

        total = max(self.active + self.out, 1)
        angle_active = 360 * self.active / total

        canvas.create_arc(10, 10, 190, 190,
                          start=90, extent=angle_active, # Start from top
                          fill=DARK_THEME["success"], outline=DARK_THEME["card_bg"]) # Added outline
        canvas.create_arc(10, 10, 190, 190,
                          start=90 + angle_active, extent=360-angle_active,
                          fill=DARK_THEME["danger"], outline=DARK_THEME["card_bg"]) # Added outline
        
        # Add legend
        legend_frame = ttk.Frame(self.stats_panel, style='KpiCard.TFrame')
        legend_frame.pack(pady=10)

        self.create_label(legend_frame, text="Active", bg=DARK_THEME["success"], fg="#ffffff", padx=5, pady=2).pack(side="left", padx=5)
        self.create_label(legend_frame, text="Out of Service", bg=DARK_THEME["danger"], fg="#ffffff", padx=5, pady=2).pack(side="left", padx=5)

    def toggle_stats_panel(self):
        if not self.stats_panel_visible:
            self.update_stats()
            self.draw_pie_chart()
            self.grid_columnconfigure(1, weight=1)
            self.stats_panel.grid()
            self.stats_panel_visible = True
        else:
            self.grid_columnconfigure(1, weight=0)
            self.stats_panel.grid_remove()
            self.stats_panel_visible = False

