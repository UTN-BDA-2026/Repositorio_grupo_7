import flet as ft
from services.client_service import client_service
from services.product_service import product_service
from database.db import get_db

class DashboardView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        
        self.primary_color = "#6200ee"
        
        self.lbl_clients = ft.Text("0", size=40, weight="bold")
        self.lbl_products = ft.Text("0", size=40, weight="bold")
        
        self.content = ft.Column(
            [
                ft.Text("📊 Escritorio Resumen", size=28, weight="bold"),
                ft.Divider(height=20, color="transparent"),
                ft.Row(
                    [
                        self._create_stat_card("👥 Clientes Activos", self.lbl_clients, "#4caf50"),
                        self._create_stat_card("📦 Productos en Catálogo", self.lbl_products, "#2196f3"),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=20
                )
            ],
            expand=True
        )

    def _create_stat_card(self, title, label_control, color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=16, color="white70"),
                    label_control
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=250,
            height=150,
            bgcolor="#2a2a2a",
            border_radius=15,
            border=ft.Border(
                left=ft.BorderSide(5, color)
            ),
            padding=20
        )

    def did_mount(self):
        self.load_stats()

    def load_stats(self):
        # Para hacer un count rápido reutilizamos el get_all con límite alto o
        # si tuviéramos un count en el service lo usaríamos.
        # En una app real haríamos un db.query(Model).count()
        with get_db() as db:
            clients = client_service.get_all(db, limit=100000)
            products = product_service.get_all(db, limit=100000)
            
        self.lbl_clients.value = str(len(clients))
        self.lbl_products.value = str(len(products))
        self.update()
