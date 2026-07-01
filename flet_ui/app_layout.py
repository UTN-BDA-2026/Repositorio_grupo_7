import flet as ft


SIDEBAR_BG = "#1e272e"
SIDEBAR_WIDTH = 240
ACCENT_COLOR = "#e74c3c"
ACCENT_HOVER = "#c0392b"
NAV_ITEM_HEIGHT = 42


class AppLayout(ft.Row):
    def __init__(self, page: ft.Page, current_user=None):
        super().__init__()
        self._page = page
        self.current_user = current_user
        self.expand = True
        self.spacing = 0
        self._active_route = "dashboard"

        self.active_view = ft.Container(expand=True)

        self.font_size_offset = 0

        self._nav_items = {
            "dashboard": ("Escritorio", ft.icons.Icons.DASHBOARD_ROUNDED, self.show_dashboard),
            "pos": ("Punto de Venta", ft.icons.Icons.POINT_OF_SALE_ROUNDED, self.show_pos),
            "purchases": ("Compras", ft.icons.Icons.SHOPPING_BAG_ROUNDED, self.show_purchases),
            "sales": ("Ventas", ft.icons.Icons.RECEIPT_LONG_ROUNDED, self.show_sales_history),
            "clients": ("Clientes", ft.icons.Icons.PEOPLE_ROUNDED, self.show_clients),
            "suppliers": ("Proveedores", ft.icons.Icons.LOCAL_SHIPPING_ROUNDED, self.show_suppliers),
            "products": ("Productos", ft.icons.Icons.INVENTORY_2_ROUNDED, self.show_products),
            "categories": ("Categorías", ft.icons.Icons.CATEGORY_ROUNDED, self.show_categories),
            "brands": ("Marcas", ft.icons.Icons.LABEL_ROUNDED, self.show_brands),
            "taxes": ("Impuestos", ft.icons.Icons.PERCENT_ROUNDED, self.show_taxes),
            "users": ("Usuarios", ft.icons.Icons.MANAGE_ACCOUNTS_ROUNDED, self.show_users),
            "audit": ("Auditoría", ft.icons.Icons.HISTORY_ROUNDED, self.show_audit),
        }

        self._nav_buttons = {}
        nav_main = []
        nav_config = []

        if self.current_user and self.current_user.branch_id:
            # Es Cajero
            main_keys = ["dashboard", "pos", "sales", "clients"]
            config_keys = []
        else:
            # Es Admin
            main_keys = ["dashboard", "pos", "purchases", "sales", "clients", "suppliers", "products"]
            config_keys = ["users", "categories", "brands", "taxes", "audit"]

        for key in main_keys:
            btn = self._build_nav_button(key)
            self._nav_buttons[key] = btn
            nav_main.append(btn)

        for key in config_keys:
            btn = self._build_nav_button(key)
            self._nav_buttons[key] = btn
            nav_config.append(btn)

        btn_shape = ft.RoundedRectangleBorder(radius=5)
        self.btn_theme = ft.IconButton(
            icon=ft.icons.Icons.DARK_MODE_ROUNDED,
            icon_color="white54",
            tooltip="Cambiar tema",
            on_click=self.toggle_theme,
        )
        self.btn_font_minus = ft.IconButton(
            icon=ft.icons.Icons.TEXT_DECREASE_ROUNDED,
            icon_color="white54",
            tooltip="Reducir letra",
            on_click=self.decrease_font,
        )
        self.btn_font_plus = ft.IconButton(
            icon=ft.icons.Icons.TEXT_INCREASE_ROUNDED,
            icon_color="white54",
            tooltip="Aumentar letra",
            on_click=self.increase_font,
        )

        self._page.appbar = ft.AppBar(
            leading=ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.icons.Icons.STORE_ROUNDED, color="white", size=28),
                        ft.Text("POS System", size=18, weight="bold", color="white"),
                    ],
                    spacing=10,
                ),
                padding=ft.Padding(left=15, top=0, right=0, bottom=0),
            ),
            leading_width=200,
            center_title=False,
            bgcolor=ACCENT_COLOR,
            actions=[
                ft.Text(f"Hola, {self.current_user.name if self.current_user else 'Admin'}", color="white", weight="bold"),
                ft.Container(width=15),
                ft.IconButton(
                    icon=ft.icons.Icons.LOGOUT_ROUNDED,
                    icon_color="white54",
                    tooltip="Cerrar Sesión",
                    on_click=self.logout,
                ),
                ft.VerticalDivider(width=1, color="white24"),
                self.btn_font_minus,
                self.btn_font_plus,
                ft.VerticalDivider(width=1, color="white24"),
                self.btn_theme,
                ft.Container(width=10),
            ],
        )

        self.sidebar = ft.Container(
            width=SIDEBAR_WIDTH,
            bgcolor=SIDEBAR_BG,
            padding=ft.Padding(left=10, top=20, right=10, bottom=20),
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text(
                            "MENÚ PRINCIPAL",
                            theme_style=ft.TextThemeStyle.LABEL_SMALL,
                            weight="bold",
                            color="white38",
                        ),
                        padding=ft.Padding(left=12, top=0, right=0, bottom=8),
                    ),
                    *nav_main,
                    ft.Container(height=15) if nav_config else ft.Container(),
                    ft.Container(
                        content=ft.Text(
                            "CONFIGURACIÓN",
                            theme_style=ft.TextThemeStyle.LABEL_SMALL,
                            weight="bold",
                            color="white38",
                        ),
                        padding=ft.Padding(left=12, top=0, right=0, bottom=8),
                    ) if nav_config else ft.Container(),
                    *nav_config,
                ],
                spacing=2,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

        self.controls = [self.sidebar, self.active_view]

    def _build_nav_button(self, key):
        label, icon, on_click = self._nav_items[key]
        is_active = key == self._active_route

        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=20, color="white" if is_active else "white54"),
                    ft.Text(
                        label,
                        theme_style=ft.TextThemeStyle.BODY_MEDIUM,
                        color="white" if is_active else "white54",
                        weight="w500" if is_active else "normal",
                    ),
                ],
                spacing=12,
            ),
            height=NAV_ITEM_HEIGHT,
            border_radius=8,
            padding=ft.Padding(left=12, top=0, right=0, bottom=0),
            bgcolor=ACCENT_COLOR if is_active else "transparent",
            on_click=lambda e, k=key: self._navigate(k),
            on_hover=self._on_nav_hover,
            ink=True,
        )

    def _on_nav_hover(self, e):
        if e.control.bgcolor == ACCENT_COLOR:
            return
        e.control.bgcolor = "#2d3a42" if e.data == "true" else "transparent"
        e.control.update()

    def _navigate(self, key):
        self._active_route = key
        _, _, handler = self._nav_items[key]
        self._refresh_nav_styles()
        handler()

    def _refresh_nav_styles(self):
        for key, container in self._nav_buttons.items():
            is_active = key == self._active_route
            label, icon_name, _ = self._nav_items[key]
            container.bgcolor = ACCENT_COLOR if is_active else "transparent"

            row = container.content
            icon_ctrl = row.controls[0]
            text_ctrl = row.controls[1]
            icon_ctrl.color = "white" if is_active else "white54"
            text_ctrl.color = "white" if is_active else "white54"
            text_ctrl.weight = "w500" if is_active else "normal"

        self.sidebar.update()

    def _update_theme(self):
        offset = self.font_size_offset
        text_color = "black" if self._page.theme_mode == ft.ThemeMode.LIGHT else "white"
        self._page.theme = ft.Theme(
            text_theme=ft.TextTheme(
                body_medium=ft.TextStyle(size=14 + offset, color=text_color),
                body_large=ft.TextStyle(size=16 + offset, color=text_color),
                label_small=ft.TextStyle(size=11 + offset, color=text_color),
                label_large=ft.TextStyle(size=14 + offset, color=text_color),
                title_medium=ft.TextStyle(size=16 + offset, color=text_color),
                title_large=ft.TextStyle(size=22 + offset, color=text_color),
                headline_medium=ft.TextStyle(size=28 + offset, color=text_color),
                display_small=ft.TextStyle(size=36 + offset, color=text_color),
            )
        )
        self._page.update()

    def increase_font(self, e):
        self.font_size_offset += 2
        self._update_theme()

    def decrease_font(self, e):
        self.font_size_offset -= 2
        self._update_theme()

    def toggle_theme(self, e):
        if self._page.theme_mode == ft.ThemeMode.LIGHT:
            self._page.theme_mode = ft.ThemeMode.DARK
            self.btn_theme.icon = ft.icons.Icons.LIGHT_MODE_ROUNDED
            self.btn_theme.tooltip = "Modo claro"
        else:
            self._page.theme_mode = ft.ThemeMode.LIGHT
            self.btn_theme.icon = ft.icons.Icons.DARK_MODE_ROUNDED
            self.btn_theme.tooltip = "Modo oscuro"
        self._update_theme()

    def show_dashboard(self, e=None):
        from flet_ui.views.dashboard_view import DashboardView
        self.active_view.content = DashboardView(self)
        self._page.update()

    def show_clients(self, e=None):
        from flet_ui.views.clients_view import ClientsView
        self.active_view.content = ClientsView(current_user=self.current_user)
        self._page.update()

    def show_suppliers(self, e=None):
        from flet_ui.views.suppliers_view import SuppliersView
        self.active_view.content = SuppliersView()
        self._page.update()

    def show_products(self, e=None):
        from flet_ui.views.products_view import ProductsView
        self.active_view.content = ProductsView()
        self._page.update()

    def show_sales_history(self, e=None):
        from flet_ui.views.sales_history_view import SalesHistoryView
        self.active_view.content = SalesHistoryView()
        self._page.update()

    def show_pos(self, e=None):
        from flet_ui.views.pos_view import POSView
        self.active_view.content = POSView()
        self._page.update()

    def show_purchases(self, e=None):
        from flet_ui.views.purchases_view import PurchasesView
        self.active_view.content = PurchasesView()
        self._page.update()

    def show_categories(self, e=None):
        from flet_ui.views.categories_view import CategoriesView
        self.active_view.content = CategoriesView()
        self._page.update()

    def show_brands(self, e=None):
        from flet_ui.views.brands_view import BrandsView
        self.active_view.content = BrandsView()
        self._page.update()

    def show_taxes(self, e=None):
        from flet_ui.views.taxes_view import TaxesView
        self.active_view.content = TaxesView()
        self._page.update()

    def show_users(self, e=None):
        from flet_ui.views.users_view import UsersView
        self.active_view.content = UsersView()
        self._page.update()

    def show_audit(self, e=None):
        from flet_ui.views.audit_view import AuditView
        self.active_view.content = AuditView()
        self._page.update()


    def logout(self, e):
        from flet_ui.views.login_view import LoginView
        self._page.controls.clear()
        self._page.appbar = None
        self._page.add(LoginView(on_login_success=lambda u: _on_login_success(self._page, u)))
        self._page.update()

def _on_login_success(page, user):
    page.controls.clear()
    layout = AppLayout(page, current_user=user)
    page.add(layout)
    layout.show_dashboard()

def main(page: ft.Page):
    page.title = "Sistema de Ventas - UTN BDA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0

    from flet_ui.views.login_view import LoginView
    page.add(LoginView(on_login_success=lambda u: _on_login_success(page, u)))


if __name__ == "__main__":
    ft.app(target=main)
