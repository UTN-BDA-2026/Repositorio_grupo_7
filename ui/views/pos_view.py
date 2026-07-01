import customtkinter as ctk

class POSView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.lbl_title = ctk.CTkLabel(
            self, 
            text="🛒 Punto de Venta (POS) - Registrar Nueva Venta", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.lbl_title.pack(pady=40, padx=20)
