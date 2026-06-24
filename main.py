import customtkinter as ctk
from ui.app import App

if __name__ == "__main__":
    # Configuramos el tema claro por defecto para CustomTkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("dark-blue")
    
    # Instanciamos y ejecutamos la aplicación
    app = App()
    app.mainloop()
