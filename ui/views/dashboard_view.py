import customtkinter as ctk
from ui.components.stat_card import StatCard
from database.db import get_db
from services import client_service, product_service, sale_service

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.lbl_dash_title = ctk.CTkLabel(
            self, 
            text="Dashboard", 
            font=ctk.CTkFont(size=14), 
            text_color=("#555555", "#a0a0b0"), 
            anchor="w"
        )
        self.lbl_dash_title.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.center_frame = ctk.CTkFrame(self, fg_color=("#ffffff", "#1c1d26"), corner_radius=15)
        self.center_frame.grid(row=1, column=0, sticky="nsew")
        self.center_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_clientes = StatCard(
            self.center_frame, 
            titulo="Clientes", 
            valor=0, 
            fg_color="#0066FF", 
            value_color="white", 
            title_color="#E0E0E0",
            height=120
        )
        self.card_clientes.grid(row=0, column=0, padx=25, pady=25, sticky="ew")
        self.card_clientes.grid_propagate(False)

        self.card_productos = StatCard(
            self.center_frame, 
            titulo="Productos", 
            valor=0, 
            fg_color="#FF6600", 
            value_color="white", 
            title_color="#E0E0E0",
            height=120
        )
        self.card_productos.grid(row=0, column=1, padx=25, pady=25, sticky="ew")
        self.card_productos.grid_propagate(False)

        self.card_ventas = StatCard(
            self.center_frame, 
            titulo="Ventas Realizadas", 
            valor=0, 
            fg_color="#00CC44", 
            value_color="white", 
            title_color="#E0E0E0",
            height=120
        )
        self.card_ventas.grid(row=0, column=2, padx=25, pady=25, sticky="ew")
        self.card_ventas.grid_propagate(False)

        self.lbl_charts = ctk.CTkLabel(
            self.center_frame, 
            text="(Espacio para gráficos de Matplotlib)", 
            text_color=("#555555", "#a0a0b0")
        )
        self.lbl_charts.grid(row=1, column=0, columnspan=3, pady=50)

        self.cargar_datos()

    def cargar_datos(self):
        with get_db() as db:
            total_clientes = client_service.count(db)
            total_productos = product_service.count(db)
            total_ventas = sale_service.count(db)

        self.card_clientes.actualizar(total_clientes)
        self.card_productos.actualizar(total_productos)
        self.card_ventas.actualizar(total_ventas)
