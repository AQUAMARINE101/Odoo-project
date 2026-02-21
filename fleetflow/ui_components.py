import tkinter as tk
from tkinter import ttk
from fleetflow.theme import DARK_THEME, FONT_FAMILY

class BasePage(tk.Frame):
    def __init__(self, master, controller, fleet_data_model, user_role, **kwargs):
        super().__init__(master, bg=DARK_THEME["bg"], **kwargs)
        self.master = master
        self.controller = controller
        self.fleet_data_model = fleet_data_model
        self.user_role = user_role
        self._subscriptions = [] # To keep track of subscriptions

        self.create_styles()

    def subscribe(self, event_type, callback):
        self.controller.subscribe(event_type, callback)
        self._subscriptions.append((event_type, callback))

    def unsubscribe_all(self):
        for event_type, callback in self._subscriptions:
            self.controller.unsubscribe(event_type, callback)
        self._subscriptions = [] # Clear the list

    def destroy(self):
        self.unsubscribe_all()
        super().destroy()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # General Entry Style
        style.configure("TEntry",
                        padding=8,
                        relief="flat",
                        fieldbackground=DARK_THEME["card_bg"],
                        foreground=DARK_THEME["card_fg"],
                        insertcolor=DARK_THEME["primary"])
        style.map("TEntry",
                  fieldbackground=[("focus", DARK_THEME["card_bg"])],
                  foreground=[("focus", DARK_THEME["card_fg"])])


        # General Button Styles
        style.configure("TButton",
                        font=(FONT_FAMILY, 11, "bold"),
                        relief="flat",
                        padding=10)
        style.map("TButton",
                  background=[("active", DARK_THEME["secondary"])],
                  foreground=[("active", DARK_THEME["fg"])])

        style.configure("Primary.TButton", background=DARK_THEME["primary"], foreground=DARK_THEME["fg"])
        style.configure("Accent.TButton", background=DARK_THEME["accent"], foreground=DARK_THEME["bg"])
        style.configure("Info.TButton", background=DARK_THEME["info"], foreground=DARK_THEME["bg"])
        style.configure("Highlight.TButton", background=DARK_THEME["highlight"], foreground=DARK_THEME["bg"])
        style.configure("Warning.TButton", background=DARK_THEME["warning"], foreground=DARK_THEME["bg"])
        style.configure("Danger.TButton", background=DARK_THEME["danger"], foreground=DARK_THEME["bg"])


        # Combobox Style
        style.configure("TCombobox",
                        padding=6,
                        fieldbackground=DARK_THEME["card_bg"],
                        foreground=DARK_THEME["card_fg"])
        style.map("TCombobox",
                  fieldbackground=[("focus", DARK_THEME["card_bg"])],
                  foreground=[("focus", DARK_THEME["card_fg"])])
        
        # Label Style (if needed, though direct tk.Label usually styled in-line)
        style.configure("TLabel",
                        background=DARK_THEME["bg"],
                        foreground=DARK_THEME["fg"],
                        font=(FONT_FAMILY, 10))
        
        # Card Label Style (for labels on card backgrounds)
        style.configure("Card.TLabel",
                        background=DARK_THEME["card_bg"],
                        foreground=DARK_THEME["card_fg"],
                        font=(FONT_FAMILY, 10))

        # Treeview (Table) Styles - General
        style.configure("Treeview",
                        background=DARK_THEME["card_bg"],
                        foreground=DARK_THEME["card_fg"],
                        fieldbackground=DARK_THEME["card_bg"],
                        font=(FONT_FAMILY, 10),
                        rowheight=25,
                        borderwidth=0,
                        relief="flat") # Ensure it's flat by default
        style.map("Treeview",
                  background=[("selected", DARK_THEME["primary"])],
                  foreground=[("selected", DARK_THEME["fg"])])

        style.configure("Treeview.Heading",
                        font=(FONT_FAMILY, 11, "bold"),
                        background=DARK_THEME["secondary"],
                        foreground=DARK_THEME["fg"],
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[("active", DARK_THEME["secondary"])])
        
        # Define the basic layout for the Treeview to ensure derived styles work
        style.layout("Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe'})
        ])

        # Driver Registry Treeview Styles
        style.configure("DriverTreeview",
                        background=DARK_THEME["card_bg"],
                        foreground=DARK_THEME["card_fg"],
                        fieldbackground=DARK_THEME["card_bg"])
        style.map('DriverTreeview',
                  background=[('selected', DARK_THEME["primary"])],
                  foreground=[('selected', '#ffffff')])
        style.layout("DriverTreeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        
        # Tags for driver status
        style.map("ON_DUTY.DriverTreeview",
                  background=[('!selected', DARK_THEME["accent"])], # Green
                  foreground=[('!selected', "#000000")])
        style.map("OFF_DUTY.DriverTreeview",
                  background=[('!selected', DARK_THEME["secondary"])], # Gray
                  foreground=[('!selected', "#ffffff")])
        style.map("SUSPENDED.DriverTreeview",
                  background=[('!selected', DARK_THEME["danger"])], # Red
                  foreground=[('!selected', "#ffffff")])
        style.map("expired_license.DriverTreeview",
                  background=[('!selected', DARK_THEME["warning"])], # Yellow
                  foreground=[('!selected', '#000000')]) # Dark text for yellow


        # Trip Dispatcher Treeview Styles
        style.configure("TripTreeview",
                        background=DARK_THEME["card_bg"],
                        foreground=DARK_THEME["card_fg"],
                        fieldbackground=DARK_THEME["card_bg"])
        style.map('TripTreeview',
                  background=[('selected', DARK_THEME["primary"])],
                  foreground=[('selected', '#ffffff')])
        style.layout("TripTreeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        # Tags for trip status
        style.map("draft.TripTreeview",
                  background=[('!selected', DARK_THEME["warning"])], # Yellow
                  foreground=[('!selected', "#000000")])
        style.map("dispatched.TripTreeview",
                  background=[('!selected', DARK_THEME["info"])], # Cyan
                  foreground=[('!selected', "#ffffff")])
        style.map("completed.TripTreeview",
                  background=[('!selected', DARK_THEME["success"])], # Green
                  foreground=[('!selected', "#ffffff")])
        style.map("cancelled.TripTreeview",
                  background=[('!selected', DARK_THEME["danger"])], # Red
                  foreground=[('!selected', "#ffffff")])
        
        # Maintenance Treeview Styles
        style.configure("MaintenanceTreeview",
                        background=DARK_THEME["card_bg"],
                        foreground=DARK_THEME["card_fg"],
                        fieldbackground=DARK_THEME["card_bg"])
        style.map('MaintenanceTreeview',
                  background=[('selected', DARK_THEME["primary"])],
                  foreground=[('selected', '#ffffff')])
        style.layout("MaintenanceTreeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        # Tags for maintenance log status
        style.map("Open.MaintenanceTreeview",
                  background=[('!selected', DARK_THEME["warning"])], # Yellow
                  foreground=[('!selected', "#000000")])
        style.map("Completed.MaintenanceTreeview",
                  background=[('!selected', DARK_THEME["accent"])], # Green
                  foreground=[('!selected', "#ffffff")])
        
        # Fuel Log Treeview Styles
        style.configure("FuelLogTreeview",
                        background=DARK_THEME["card_bg"],
                        foreground=DARK_THEME["card_fg"],
                        fieldbackground=DARK_THEME["card_bg"])
        style.map('FuelLogTreeview',
                  background=[('selected', DARK_THEME["primary"])],
                  foreground=[('selected', '#ffffff')])
        style.layout("FuelLogTreeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        # Analytics & Reports Treeview Styles
        style.configure("AnalyticsTreeview",
                        background=DARK_THEME["card_bg"],
                        foreground=DARK_THEME["card_fg"],
                        fieldbackground=DARK_THEME["card_bg"])
        style.map('AnalyticsTreeview',
                  background=[('selected', DARK_THEME["primary"])],
                  foreground=[('selected', '#ffffff')])
        style.layout("AnalyticsTreeview", [('Treeview.treearea', {'sticky': 'nswe'})])


    def create_label(self, parent, text, font_size=10, font_weight="normal", **kwargs):
        # For ttk.Label, font can be passed directly.
        # Other properties like foreground/background are controlled by styles.
        style_name = kwargs.pop('style', 'TLabel') # Use a default style
        final_font = (FONT_FAMILY, font_size, font_weight)
        return ttk.Label(parent, text=text, font=final_font, style=style_name, **kwargs)

    def create_button(self, parent, text, command, style="TButton", **kwargs):
        # Use ttk.Button and its styling mechanism
        btn = ttk.Button(parent,
                       text=text,
                       command=command,
                       style=style,
                       **kwargs)
        return btn

    def create_back_button(self, parent_frame):
        back_btn = self.create_button(parent_frame,
                                      text="⬅ Back to Main Menu",
                                      command=self.master.destroy,
                                      style="Secondary.TButton")
        return back_btn
