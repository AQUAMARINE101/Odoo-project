import tkinter as tk
from fleetflow.theme import DARK_THEME, FONT_FAMILY
from fleetflow.main import FleetFlowLogin
from fleetflow.main_menu import MainMenu
from fleetflow.fleet_data_model import FleetDataModel # Import FleetDataModel
import traceback # Import traceback
import sys # Import sys
from tkinter import messagebox # Import messagebox for error dialogs

# =========================================================
# GLOBAL ERROR HANDLER
# =========================================================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    error_text = "".join(
        traceback.format_exception(exc_type, exc_value, exc_traceback)
    )
    print("UNHANDLED ERROR:\n", error_text)
    try:
        messagebox.showerror("Critical Error",
                             f"An unexpected error occurred:\n\n{exc_value}")
    except:
        pass # If messagebox fails, just print to console

sys.excepthook = global_exception_handler

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FleetFlow Application")
        self.geometry("800x600")
        self.resizable(False, False) # Make the window non-resizable
        self.config(bg=DARK_THEME["bg"])
        
        # Configure Tkinter error reporting
        def tk_exception_handler(exc_type, exc_value, exc_traceback):
            global_exception_handler(exc_type, exc_value, exc_traceback)
        self.report_callback_exception = tk_exception_handler

        self.callbacks = {} # Initialize the callbacks dictionary
        self.fleet_data_model = FleetDataModel() # Instantiate FleetDataModel

        self._frame = None
        self.switch_frame(FleetFlowLogin)

    def subscribe(self, event_type, callback):
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)

    def publish(self, event_type, data=None):
        if event_type in self.callbacks:
            # Iterate over a copy of the list to allow unsubscription during iteration
            for callback in list(self.callbacks[event_type]):
                # Check if the callback's object has been destroyed
                if hasattr(callback, '__self__') and not callback.__self__.winfo_exists():
                    self.unsubscribe(event_type, callback)
                    continue
                callback(data)

    def unsubscribe(self, event_type, callback):
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            if not self.callbacks[event_type]: # Remove event_type if no callbacks left
                del self.callbacks[event_type]

    def switch_frame(self, frame_class, **kwargs):
        # Pass self (controller) and fleet_data_model to the new frame
        new_frame = frame_class(self, self, fleet_data_model=self.fleet_data_model, **kwargs)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill="both", expand=True)

    def logout(self):
        self.switch_frame(FleetFlowLogin)

if __name__ == "__main__":
    app = App()
    app.mainloop()
