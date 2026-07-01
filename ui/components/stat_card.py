import customtkinter as ctk

class StatCard(ctk.CTkFrame):
    def __init__(
        self, 
        parent, 
        titulo: str, 
        valor: int = 0, 
        title_color = ("gray40", "gray70"),
        value_color = ("gray10", "gray90"),
        title_size: int = 13,
        value_size: int = 36,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.lbl_titulo = ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(size=title_size),
            text_color=title_color,
        )
        self.lbl_titulo.pack(pady=(15, 2))

        self.lbl_valor = ctk.CTkLabel(
            self,
            text=str(valor),
            font=ctk.CTkFont(size=value_size, weight="bold"),
            text_color=value_color,
        )
        self.lbl_valor.pack(pady=(2, 15))

    def actualizar(self, nuevo_valor: int):
        self.lbl_valor.configure(text=str(nuevo_valor))
