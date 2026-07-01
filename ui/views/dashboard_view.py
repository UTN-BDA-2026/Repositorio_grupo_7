import flet as ft
from services.client_service import client_service
from services.product_service import product_service
from services.sale_service import sale_service
from services.category_service import category_service
from services.brand_service import brand_service
from services.tax_service import tax_service
from database.db import get_db


CARD_CONFIGS = [
    {
        "key": "pos",
        "label": "Punto de Venta",
        "icon": ft.icons.Icons.POINT_OF_SALE_ROUNDED,
        "color": "#e74c3c",
        "nav_key": "pos",
    },
    {
        "key": "products",
        "label": "Productos",
        "icon": ft.icons.Icons.INVENTORY_2_ROUNDED,
        "color": "#e67e22",
        "nav_key": "products",
    },
    {
        "key": "sales",
        "label": "Ventas",
        "icon": ft.icons.Icons.RECEIPT_LONG_ROUNDED,
        "color": "#f1c40f",
        "nav_key": "sales",
    },
    {
        "key": "clients",
        "label": "Clientes",
        "icon": ft.icons.Icons.PEOPLE_ROUNDED,
        "color": "#2ecc71",
        "nav_key": "clients",
    },
    {
        "key": "categories",
        "label": "Categorías",
        "icon": ft.icons.Icons.CATEGORY_ROUNDED,
        "color": "#9b59b6",
        "nav_key": "categories",
    },
    {
        "key": "brands",
        "label": "Marcas",
        "icon": ft.icons.Icons.LABEL_ROUNDED,
        "color": "#3498db",
        "nav_key": "brands",
    },
    {
        "key": "taxes",
        "label": "Impuestos",
        "icon": ft.icons.Icons.PERCENT_ROUNDED,
        "color": "#1abc9c",
        "nav_key": "taxes",
    },
    {
        "key": "users",
        "label": "Usuarios",
        "icon": ft.icons.Icons.MANAGE_ACCOUNTS_ROUNDED,
        "color": "#9b59b6",
        "nav_key": "users",
    },
]

SERVICE_MAP = {
    "products": product_service,
    "clients": client_service,
    "sales": sale_service,
    "categories": category_service,
    "brands": brand_service,
    "taxes": tax_service,
    "users": __import__('services.user_service', fromlist=['user_service']).user_service,
}


class DashboardView(ft.Container):
    def __init__(self, app_layout=None):
        super().__init__()
        self.expand = True
        self.padding = 30
        self._app_layout = app_layout

        self._count_labels = {}
        self._cards = []

        for cfg in CARD_CONFIGS:
            if self._app_layout and cfg["nav_key"] not in self._app_layout._nav_buttons:
                continue

            count_label = ft.Text("—", size=36, weight="bold", color="white")
            self._count_labels[cfg["key"]] = count_label

            card = ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                count_label,
                                ft.Text(cfg["label"], size=16, weight="w500", color="white"),
                            ],
                            spacing=2,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Icon(cfg["icon"], size=64, color="white"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=cfg["color"],
                border_radius=10,
                padding=ft.Padding(left=20, top=18, right=20, bottom=18),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color="#26000000",
                    offset=ft.Offset(0, 3),
                ),
                on_click=lambda e, nav=cfg["nav_key"]: self._go_to(nav),
                on_hover=self._on_card_hover,
                ink=True,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
                expand=True,
            )
            self._cards.append(card)

        cards_grid = ft.ResponsiveRow(
            [
                ft.Container(card, col={"xs": 12, "sm": 6, "md": 4, "lg": 3})
                for card in self._cards
            ],
            spacing=15,
            run_spacing=15,
        )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Escritorio", size=28, weight="bold"),
                                ft.Text(
                                    "Resumen general del sistema",
                                    size=14,
                                    color="grey",
                                ),
                            ],
                            spacing=2,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=25, color="transparent"),
                ft.Text(
                    "ENLACES RÁPIDOS",
                    size=12,
                    weight="bold",
                    color="grey",
                ),
                ft.Container(height=5),
                cards_grid,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def did_mount(self):
        self._load_stats()

    def _load_stats(self):
        with get_db() as db:
            counts = {}
            for key, service in SERVICE_MAP.items():
                try:
                    counts[key] = service.count(db)
                except Exception:
                    counts[key] = 0

        counts["pos"] = counts.get("sales", 0)

        for key, label in self._count_labels.items():
            value = counts.get(key, 0)
            label.value = str(value)

        self.update()

    def _go_to(self, nav_key):
        if self._app_layout:
            self._app_layout._active_route = nav_key
            self._app_layout._refresh_nav_styles()
            _, _, handler = self._app_layout._nav_items[nav_key]
            handler()

    def _on_card_hover(self, e):
        if e.data == "true":
            e.control.scale = 1.03
        else:
            e.control.scale = 1.0
        e.control.update()
