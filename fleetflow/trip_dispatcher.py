import tkinter as tk
from tkinter import ttk, messagebox
from enum import Enum
from fleetflow.theme import DARK_THEME, LIGHT_THEME, FONT_FAMILY
from fleetflow.permissions import has_permission, TRIP_DISPATCHER_PERMISSIONS
from fleetflow.fleet_data_model import FleetDataModel, Vehicle, Driver, Trip, TripStatus # Import FleetDataModel and models
from fleetflow.ui_components import BasePage # Import BasePage
from datetime import datetime # Import datetime

# -------------------------------
# UI Application
# -------------------------------
class DispatcherApp(BasePage): # Inherit from BasePage
    def __init__(self, master, controller, fleet_data_model, user_role="Guest"): # Accept controller and fleet_data_model
        super().__init__(master, controller, fleet_data_model, user_role) # Call BasePage.__init__
        self.current_trip = None # Use this to store the currently active trip object

        self.create_ui()
        self.refresh_dropdowns() # This will now also refresh the trip table
        self.subscribe("vehicle_updated", self.refresh_dropdowns) # Subscribe to vehicle updates
        self.subscribe("driver_updated", self.refresh_dropdowns) # Subscribe to driver updates
        self.subscribe("trip_updated", self.refresh_dropdowns) # Subscribe to trip updates

    def create_ui(self):
        self.pack(fill="both", expand=True)
        main_frame = ttk.Frame(self, style='TripDispatcher.TFrame')
        main_frame.pack(fill="both", expand=True)

        # Header
        header = self.create_label(main_frame, text="🚚 Smart Trip Dispatcher",
                          font_size=20, font_weight="bold")
        header.pack(pady=15)

        # Two main sections: Form on left, Trip List on right
        content_frame = ttk.Frame(main_frame, style='TripDispatcher.TFrame')
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)

        # Left Section: Trip Creation Form
        form_frame = ttk.Frame(content_frame, style='TripCard.TFrame')
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        form_frame.grid_columnconfigure(1, weight=1)

        self.create_label(form_frame, text="Create New Trip",
                 font_size=14, font_weight="bold",
                 style='TripCard.TLabel').grid(row=0, column=0, columnspan=2, pady=10)

        row_idx = 1

        # Vehicle Selection
        self.create_label(form_frame, text="🚛 Select Vehicle",
                 style='TripCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.vehicle_var = tk.StringVar()
        self.vehicle_dropdown = ttk.Combobox(form_frame, textvariable=self.vehicle_var,
                                             state="readonly" if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["create"]) else "disabled")
        self.vehicle_dropdown.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Driver Selection
        self.create_label(form_frame, text="👨‍✈️ Select Driver",
                 style='TripCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.driver_var = tk.StringVar()
        self.driver_dropdown = ttk.Combobox(form_frame, textvariable=self.driver_var,
                                            state="readonly" if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["create"]) else "disabled")
        self.driver_dropdown.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Cargo
        self.create_label(form_frame, text="📦 Cargo Weight (kg)",
                 style='TripCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.cargo_entry = ttk.Entry(form_frame,
                                    state="normal" if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["create"]) else "disabled")
        self.cargo_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Start Odometer
        self.create_label(form_frame, text="Start Odometer",
                 style='TripCard.TLabel').grid(row=row_idx, column=0, padx=5, pady=(5,0), sticky="w")
        self.start_odometer_entry = ttk.Entry(form_frame,
                                             state="normal" if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["create"]) else "disabled")
        self.start_odometer_entry.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        row_idx += 1

        # Create Button
        self.create_button(form_frame, text="✨ Create Trip",
                  command=self.create_trip,
                  style="Highlight.TButton",
                  state="normal" if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["create"]) else "disabled").grid(row=row_idx, column=0, columnspan=2, pady=15)
        row_idx += 1

        # Current Trip Status Display
        self.status_label = self.create_label(form_frame,
                                     text="No Trip Selected",
                                     font_size=12, font_weight="bold",
                                     style='TripCard.TLabel')
        self.status_label.grid(row=row_idx, column=0, columnspan=2, pady=(10,5))
        row_idx += 1

        # Lifecycle Buttons Frame
        btn_frame = ttk.Frame(form_frame, style='TripCard.TFrame')
        btn_frame.grid(row=row_idx, column=0, columnspan=2, pady=10)
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.dispatch_btn = self.create_button(btn_frame, text="🚀 Dispatch",
                  command=self.dispatch_trip,
                  style="Info.TButton",
                  state="disabled") # Disabled by default, enabled based on selected trip status
        self.dispatch_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.complete_btn = self.create_button(btn_frame, text="✅ Complete",
                  command=self.complete_trip,
                  style="Accent.TButton",
                  state="disabled") # Disabled by default
        self.complete_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.cancel_btn = self.create_button(btn_frame, text="❌ Cancel",
                  command=self.cancel_trip,
                  style="Danger.TButton",
                  state="disabled") # Disabled by default
        self.cancel_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Right Section: Trip List
        list_frame = ttk.Frame(content_frame, style='TripDispatcher.TFrame')
        list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)


        self.create_label(list_frame, text="Active & Pending Trips",
                 font_size=14, font_weight="bold").pack(pady=10)

        columns = ("ID", "Vehicle", "Driver", "Cargo (kg)", "Start Odo", "Status")
        self.trip_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="TripTreeview")

        for col in columns:
            self.trip_tree.heading(col, text=col)
            self.trip_tree.column(col, width=100, anchor="center")
        
        # Adjust column widths for better readability
        self.trip_tree.column("ID", width=70)
        self.trip_tree.column("Vehicle", width=80)
        self.trip_tree.column("Driver", width=80)
        self.trip_tree.column("Cargo (kg)", width=80)
        self.trip_tree.column("Start Odo", width=80)
        self.trip_tree.column("Status", width=80)

        self.trip_tree.pack(fill="both", expand=True)
        self.trip_tree.bind("<<TreeviewSelect>>", self.load_selected_trip)

        self.refresh_dropdowns() # Initial population

        # Back button
        self.create_back_button(main_frame).pack(side="bottom", pady=10)

    def refresh_dropdowns(self, *args): # *args to accept event data if published
        # Get available vehicles from FleetDataModel
        available_vehicles = [v.vehicle_id for v in self.fleet_data_model.get_all_vehicles() if v.available]
        self.vehicle_dropdown["values"] = available_vehicles
        if available_vehicles:
            if self.vehicle_var.get() not in available_vehicles:
                self.vehicle_var.set(available_vehicles[0])
        else:
            self.vehicle_var.set("")

        # Get available drivers from FleetDataModel
        available_drivers = [d.driver_id for d in self.fleet_data_model.get_all_drivers() if d.available]
        self.driver_dropdown["values"] = available_drivers
        if available_drivers:
            if self.driver_var.get() not in available_drivers:
                self.driver_var.set(available_drivers[0])
        else:
            self.driver_var.set("")
        
        self.refresh_trip_list() # Also refresh the trip list when vehicles or drivers update

    def refresh_trip_list(self):
        for row in self.trip_tree.get_children():
            self.trip_tree.delete(row)
        
        # Display active and pending trips
        for trip in self.fleet_data_model.get_all_trips():
            if trip.status not in [TripStatus.COMPLETED, TripStatus.CANCELLED]:
                self.trip_tree.insert("", "end",
                                      iid=trip.trip_id, # Use trip_id as the item identifier
                                      values=(trip.trip_id[:5] + "...", # Truncate for display
                                              trip.vehicle_id,
                                              trip.driver_id,
                                              trip.cargo_weight,
                                              trip.start_odometer,
                                              trip.status.value),
                                      tags=(trip.status.name.lower() + ".TripTreeview",)) # Apply status tag for styling
        self.update_lifecycle_buttons() # Update button states after refresh


    def load_selected_trip(self, event):
        selected_item = self.trip_tree.selection()
        if not selected_item:
            self.current_trip = None
            self.update_status_display()
            self.update_lifecycle_buttons()
            return

        trip_id_prefix = self.trip_tree.item(selected_item[0])["values"][0] # Get truncated ID
        # Find the full trip ID from the model based on the prefix (or store full ID in iid)
        # Using iid directly for lookup is better if full ID is stored there
        full_trip_id = selected_item[0] 
        self.current_trip = self.fleet_data_model.get_trip(full_trip_id)
        
        if self.current_trip:
            self.update_status_display()
            self.update_lifecycle_buttons()
            # Populate form fields for the selected trip (optional, for editing existing trip)
            self.vehicle_var.set(self.current_trip.vehicle_id)
            self.driver_var.set(self.current_trip.driver_id)
            self.cargo_entry.delete(0, tk.END)
            self.cargo_entry.insert(0, str(self.current_trip.cargo_weight))
            self.start_odometer_entry.delete(0, tk.END)
            self.start_odometer_entry.insert(0, str(self.current_trip.start_odometer))
            
            # Disable creation fields when an existing trip is selected for management
            self.cargo_entry.config(state="disabled")
            self.start_odometer_entry.config(state="disabled")
            self.vehicle_dropdown.config(state="disabled")
            self.driver_dropdown.config(state="disabled")
        else:
            # Clear selection if no trip found (shouldn't happen with iid)
            self.trip_tree.selection_remove(selected_item[0])
            self.current_trip = None
            self.update_status_display()
            self.update_lifecycle_buttons()

    def update_status_display(self):
        if self.current_trip:
            status = self.current_trip.status.value
            color_map = {
                "Draft": DARK_THEME["warning"],
                "Dispatched": DARK_THEME["info"],
                "Completed": DARK_THEME["success"],
                "Cancelled": DARK_THEME["danger"]
            }
            color = color_map.get(status, DARK_THEME["fg"])
            self.status_label.config(text=f"Selected Trip Status: {status}",
                                     foreground=color)

        else:
            self.status_label.config(text="No Trip Selected", foreground=DARK_THEME["fg"])

    def update_lifecycle_buttons(self):
        # Disable all buttons by default
        self.dispatch_btn.config(state="disabled")
        self.complete_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")

        if self.current_trip and has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["update"]):
            current_status = self.current_trip.status

            if current_status == TripStatus.DRAFT:
                if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["dispatch"]):
                    self.dispatch_btn.config(state="normal")
                if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["cancel"]):
                    self.cancel_btn.config(state="normal")
            elif current_status == TripStatus.DISPATCHED:
                if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["complete"]):
                    self.complete_btn.config(state="normal")
                if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["cancel"]):
                    self.cancel_btn.config(state="normal")
            # For Completed and Cancelled trips, all lifecycle buttons remain disabled
        
        # Always allow creating new trips if permission exists
        if has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["create"]):
            self.cargo_entry.config(state="normal")
            self.start_odometer_entry.config(state="normal")
            self.vehicle_dropdown.config(state="readonly")
            self.driver_dropdown.config(state="readonly")


    def create_trip(self):
        if not has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["create"]):
            messagebox.showerror("Permission Denied", "You do not have permission to create trips.")
            return

        vehicle_id = self.vehicle_var.get()
        driver_id = self.driver_var.get()

        if not vehicle_id or not driver_id:
            messagebox.showerror("Error", "Select vehicle and driver!")
            return

        try:
            cargo_weight = float(self.cargo_entry.get())
            if cargo_weight <= 0:
                raise ValueError("Cargo weight must be positive.")
            
            start_odometer = float(self.start_odometer_entry.get()) # Get start odometer
            # Validate start odometer against current vehicle odometer if possible
            vehicle = self.fleet_data_model.get_vehicle(vehicle_id)
            if vehicle and start_odometer < vehicle.odometer:
                response = messagebox.askyesno("Warning", 
                                              f"Start odometer ({start_odometer}) is less than vehicle's current odometer ({vehicle.odometer}). Do you wish to proceed?")
                if not response:
                    return

        except ValueError as e:
            messagebox.showerror("Error", f"Enter valid positive cargo weight and non-negative start odometer! ({e})")
            return

        try:
            new_trip = Trip(vehicle_id=vehicle_id, driver_id=driver_id, cargo_weight=cargo_weight, start_odometer=start_odometer) # Pass start_odometer
            self.fleet_data_model.add_trip(new_trip)
            self.current_trip = new_trip # Set current trip
            self.update_status_display()
            self.update_lifecycle_buttons()
            messagebox.showinfo("Success", "Trip Created Successfully!")
            self.refresh_dropdowns() # Refresh dropdowns and trip list
            self.publish("vehicle_updated") # Notify vehicle registry
            self.publish("driver_updated") # Notify driver registry
            self.publish("trip_updated") # Notify dashboard
            
            # Clear form fields after successful creation
            self.cargo_entry.delete(0, tk.END)
            self.start_odometer_entry.delete(0, tk.END)

        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def dispatch_trip(self):
        if not has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["dispatch"]):
            messagebox.showerror("Permission Denied", "You do not have permission to dispatch trips.")
            return

        if self.current_trip:
            try:
                self.fleet_data_model.update_trip_status(self.current_trip.trip_id, TripStatus.DISPATCHED)
                self.update_status_display()
                self.update_lifecycle_buttons()
                messagebox.showinfo("Success", f"Trip {self.current_trip.trip_id} Dispatched!")
                self.refresh_dropdowns() # Refresh dropdowns and trip list
                self.publish("vehicle_updated") # Notify vehicle registry
                self.publish("driver_updated") # Notify driver registry
                self.publish("trip_updated") # Notify dashboard
            except ValueError as e:
                messagebox.showerror("Action Forbidden", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        else:
            messagebox.showwarning("No Trip", "No trip to dispatch.")


    def complete_trip(self):
        if not has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["complete"]):
            messagebox.showerror("Permission Denied", "You do not have permission to complete trips.")
            return

        if self.current_trip:
            # Prompt for end odometer
            end_odometer_dialog = tk.Toplevel(self.root)
            end_odometer_dialog.title("Enter End Odometer")
            end_odometer_dialog.geometry("350x200")
            end_odometer_dialog.transient(self.root) # Make it on top of the main window
            end_odometer_dialog.grab_set() # Disable interaction with other windows
            end_odometer_dialog.resizable(False, False)
            end_odometer_dialog.configure(bg=DARK_THEME["bg"]) # Apply background color

            # Apply styling to dialog widgets
            dialog_frame = ttk.Frame(end_odometer_dialog, style='TripDispatcher.TFrame')
            dialog_frame.pack(padx=10, pady=10, fill="both", expand=True)

            self.create_label(dialog_frame, text="Enter End Odometer:",
                              style='TripDispatcher.TLabel').pack(pady=(10,5))
            end_odometer_entry = ttk.Entry(dialog_frame, style='TripDispatcher.TEntry')
            end_odometer_entry.pack(pady=5)
            end_odometer_entry.focus_set() # Focus on the entry field

            def submit_end_odometer():
                try:
                    end_odo = float(end_odometer_entry.get())
                    
                    self.fleet_data_model.update_trip_status(self.current_trip.trip_id, TripStatus.COMPLETED, end_odometer=end_odo)
                    self.update_status_display()
                    self.update_lifecycle_buttons()
                    self.refresh_dropdowns()
                    messagebox.showinfo("Success", f"Trip {self.current_trip.trip_id} Completed!")
                    self.publish("vehicle_updated") # Notify vehicle registry
                    self.publish("driver_updated") # Notify driver registry
                    self.publish("trip_updated") # Notify dashboard
                    end_odometer_dialog.destroy()
                except ValueError as e:
                    messagebox.showerror("Invalid Input", str(e))
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")

            ttk.Button(dialog_frame, text="Submit", command=submit_end_odometer, style='TButton').pack(pady=10) # Use TButton style
            self.root.wait_window(end_odometer_dialog) # Wait for the dialog to close
        else:
            messagebox.showwarning("No Trip", "No trip to complete.")

    def cancel_trip(self):
        if not has_permission(self.user_role, TRIP_DISPATCHER_PERMISSIONS["cancel"]):
            messagebox.showerror("Permission Denied", "You do not have permission to cancel trips.")
            return

        if self.current_trip:
            try:
                self.fleet_data_model.update_trip_status(self.current_trip.trip_id, TripStatus.CANCELLED)
                self.update_status_display()
                self.update_lifecycle_buttons()
                messagebox.showinfo("Success", f"Trip {self.current_trip.trip_id} Cancelled!")
                self.refresh_dropdowns() # Refresh dropdowns and trip list
                self.publish("vehicle_updated") # Notify vehicle registry
                self.publish("driver_updated") # Notify driver registry
                self.publish("trip_updated") # Notify dashboard
            except ValueError as e:
                messagebox.showerror("Action Forbidden", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        else:
            messagebox.showwarning("No Trip", "No trip to cancel.")

