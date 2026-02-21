import tkinter as tk
from tkinter import ttk, messagebox
from fleetflow.main_menu import MainMenu
from fleetflow.theme import DARK_THEME, LIGHT_THEME, FONT_FAMILY
from fleetflow.fleet_data_model import FleetDataModel # Import FleetDataModel
from fleetflow.ui_components import BasePage # Import BasePage

# -----------------------------
# Main App
# -----------------------------
class FleetFlowLogin(BasePage): # Inherit from BasePage
    def __init__(self, master, controller, fleet_data_model, **kwargs): # No user_role for login in __init__
        super().__init__(master, controller, fleet_data_model, user_role="Guest", **kwargs) # Call BasePage.__init__ with a default user_role for initial setup
        self.master = master
        self.controller = controller
        self.fleet_data_model = fleet_data_model

        self.build_ui()

    # -----------------------------
    # UI Layout
    # -----------------------------
    def build_ui(self):
        # The BasePage is already a frame that fills the master.
        # We'll create a central frame for the login form.
        self.pack(fill="both", expand=True) # Pack the BasePage itself.

        # Main Card Frame
        self.card = ttk.Frame(self, style='TFrame')
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=450, height=500) # Increased height

        # Configure grid for the card
        self.card.grid_columnconfigure(0, weight=1)

        # Logo / Title
        title = self.create_label(self.card, "🚛 FleetFlow", font_size=24, font_weight="bold", style='Card.TLabel')
        title.grid(row=0, column=0, pady=(40, 10), sticky="n")

        subtitle = self.create_label(self.card, "Fleet & Logistics Management System", font_size=10, style='Card.TLabel')
        subtitle.grid(row=1, column=0, pady=(0, 30), sticky="n")

        # Email
        email_label = self.create_label(self.card, "Email Address", font_size=10, style='Card.TLabel')
        email_label.grid(row=2, column=0, padx=45, pady=(10,0), sticky="w")

        self.email_entry = ttk.Entry(self.card, style='TEntry')
        self.email_entry.grid(row=3, column=0, padx=45, pady=5, sticky="ew")

        # Password
        password_label = self.create_label(self.card, "Password", font_size=10, style='Card.TLabel')
        password_label.grid(row=4, column=0, padx=45, pady=(15, 0), sticky="w")

        self.password_entry = ttk.Entry(self.card, show="*", style='TEntry')
        self.password_entry.grid(row=5, column=0, padx=45, pady=5, sticky="ew")

        # Role
        role_label = self.create_label(self.card, "Select Role", font_size=10, style='Card.TLabel')
        role_label.grid(row=6, column=0, padx=45, pady=(15, 0), sticky="w")

        self.role_var = tk.StringVar()
        self.role_combo = ttk.Combobox(
            self.card,
            textvariable=self.role_var,
            values=["Manager", "Dispatcher", "Safety", "Finance"],
            state="readonly",
            style='TCombobox'
        )
        self.role_combo.grid(row=7, column=0, padx=45, pady=5, sticky="ew")
        self.role_combo.current(0)

        # Login Button
        self.login_btn = self.create_button(self.card, "LOGIN", self.authenticate)
        self.login_btn.grid(row=8, column=0, pady=40, ipadx=20, ipady=10)

        # Forgot Password
        forgot = self.create_label(self.card, "Forgot Password?", font_size=9, style='Card.TLabel')
        forgot.grid(row=9, column=0, sticky="n")
        forgot.bind("<Button-1>", self.forgot_password)
        forgot.config(cursor="hand2")

        # Footer
        footer = self.create_label(self, "© 2026 FleetFlow Logistics Systems", font_size=8)
        footer.pack(side="bottom", pady=10)



    # -----------------------------
    # Authentication Logic
    # -----------------------------
    def authenticate(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        selected_role = self.role_var.get()

        user = self.fleet_data_model.get_user(email) # Use FleetDataModel

        if user:
            if user.password == password and user.role == selected_role:
                messagebox.showinfo("Access Granted", f"Welcome {selected_role}!")
                self.controller.switch_frame(MainMenu, user_role=selected_role)
            else:
                messagebox.showerror("Login Failed", "Invalid credentials or role mismatch.")
        else:
            messagebox.showerror("Login Failed", "User not found.")

    def forgot_password(self, event):
        messagebox.showinfo("Password Reset", "Please contact system administrator.")
