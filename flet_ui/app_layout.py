import flet as ft
from flet_ui.views.clients_view import ClientsView

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        self.expand = True
        self.spacing = 0
        
        # Container for the active view
        self.active_view = ft.Container(expand=True)
        
        # Theme Switcher Button
        btn_shape = ft.RoundedRectangleBorder(radius=5)
        self.btn_theme = ft.ElevatedButton(
            "Modo Oscuro", 
            icon=ft.icons.Icons.DARK_MODE,
            on_click=self.toggle_theme,
            style=ft.ButtonStyle(shape=btn_shape)
        )
        
        # Font Size Controls
        self.font_size_offset = 0
        
        self.btn_font_minus = ft.TextButton(
            content=ft.Row([ft.Text("A", size=12), ft.Text("-")], spacing=2),
            on_click=self.decrease_font, 
            tooltip="Reducir Letra",
            style=ft.ButtonStyle(shape=btn_shape)
        )
        
        self.btn_font_plus = ft.TextButton(
            content=ft.Row([ft.Text("A", size=18), ft.Text("+")], spacing=2),
            on_click=self.increase_font, 
            tooltip="Aumentar Letra",
            style=ft.ButtonStyle(shape=btn_shape)
        )
        
        # Top App Bar for Global Controls
        self._page.appbar = ft.AppBar(
            title=ft.Text("Sistema de Ventas"),
            center_title=False,
            bgcolor="surfacevariant",
            actions=[
                self.btn_font_minus,
                self.btn_font_plus,
                self.btn_theme,
                ft.Container(width=10) # Padding
            ]
        )
        
        # Sidebar
        self.sidebar = ft.Container(
            width=250,
            bgcolor="surfacevariant",
            padding=20,
            content=ft.Column(
                [
                    ft.Text("Menu Principal", color="gray", weight="bold"),
                    ft.Divider(height=10, color="transparent"),
                    self._create_nav_button("📊 Escritorio", self.show_dashboard),
                    self._create_nav_button("👥 Clientes", self.show_clients),
                    self._create_nav_button("📦 Productos", self.show_products),
                ]
            )
        )
        
        self.controls = [self.sidebar, self.active_view]

    def _update_theme(self):
        offset = self.font_size_offset
        # Forzamos el color según el modo para que no se ponga gris al sobreescribir el Theme
        text_color = "black" if self._page.theme_mode == ft.ThemeMode.LIGHT else "white"
        
        self._page.theme = ft.Theme(
            text_theme=ft.TextTheme(
                body_medium=ft.TextStyle(size=14 + offset, color=text_color),
                body_large=ft.TextStyle(size=16 + offset, color=text_color),
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

    def _create_nav_button(self, text, on_click):
        return ft.TextButton(
            text, 
            style=ft.ButtonStyle(
                alignment=ft.Alignment(-1, 0),
                shape=ft.RoundedRectangleBorder(radius=5)
            ),
            on_click=on_click
        )

    def toggle_theme(self, e):
        if self._page.theme_mode == ft.ThemeMode.LIGHT:
            self._page.theme_mode = ft.ThemeMode.DARK
            self.btn_theme.text = "Modo Claro"
            self.btn_theme.icon = ft.icons.Icons.LIGHT_MODE
        else:
            self._page.theme_mode = ft.ThemeMode.LIGHT
            self.btn_theme.text = "Modo Oscuro"
            self.btn_theme.icon = ft.icons.Icons.DARK_MODE
        
        self._update_theme()

    def show_clients(self, e=None):
        from flet_ui.views.clients_view import ClientsView
        self.active_view.content = ClientsView()
        self._page.update()

    def show_dashboard(self, e=None):
        from flet_ui.views.dashboard_view import DashboardView
        self.active_view.content = DashboardView()
        self._page.update()

    def show_products(self, e=None):
        from flet_ui.views.products_view import ProductsView
        self.active_view.content = ProductsView()
        self._page.update()

def main(page: ft.Page):
    page.title = "Sistema de Ventas - UTN BDA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0

    layout = AppLayout(page)
    page.add(layout)
    
    # Mostrar clientes por defecto
    layout.show_clients()

if __name__ == "__main__":
    ft.app(target=main)
