import flet as ft
from services.brand_service import brand_service
from database.db import get_db
from flet_ui.components.paginated_table import PaginatedTable


class BrandsView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        self.primary_color = "#6200ee"
        self.selected_brand = None

        btn_shape = ft.RoundedRectangleBorder(radius=5)
        self.btn_add = ft.FilledButton(
            "➕ Agregar",
            on_click=self.open_form_modal,
            style=ft.ButtonStyle(bgcolor=self.primary_color, color="white", shape=btn_shape)
        )
        self.btn_view = ft.ElevatedButton(
            "👁 Ver Seleccionado",
            on_click=lambda e: self.view_selected(self.selected_brand),
            disabled=True,
            style=ft.ButtonStyle(shape=btn_shape)
        )
        self.btn_delete = ft.ElevatedButton(
            "🗑 Eliminar Seleccionado",
            on_click=lambda e: self.confirm_delete(self.selected_brand.id),
            disabled=True,
            color="red",
            style=ft.ButtonStyle(shape=btn_shape)
        )

        self.table = PaginatedTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Slug")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Activo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            fetch_data_callback=self._fetch_brands,
            build_cells_callback=self._build_brand_cells,
            on_row_click=self._on_row_selected,
            on_row_double_click=self.view_selected,
            page_size=15
        )

        self.content = ft.Column(
            [
                ft.Text("🏷 Administración de Marcas", size=28, weight="bold"),
                ft.Row(
                    [self.btn_add, self.btn_view, self.btn_delete],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10
                ),
                ft.Divider(height=5, color="transparent"),
                self.table,
            ],
            expand=True
        )

    def _fetch_brands(self, skip, limit):
        with get_db() as db:
            return brand_service.get_all(db, skip=skip, limit=limit)

    def _on_row_selected(self, brand):
        self.selected_brand = brand
        has_selection = brand is not None
        self.btn_view.disabled = not has_selection
        self.btn_delete.disabled = not has_selection
        self.update()

    def _build_brand_cells(self, brand):
        return [
            ft.DataCell(ft.Text(brand.name)),
            ft.DataCell(ft.Text(brand.slug)),
            ft.DataCell(ft.Text(brand.description or "-")),
            ft.DataCell(ft.Text("Sí" if brand.is_active else "No")),
            ft.DataCell(
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.Icons.EDIT,
                        icon_color="blue",
                        tooltip="Editar",
                        on_click=lambda e, b=brand: self.open_form_modal(e, b.id)
                    ),
                    ft.IconButton(
                        icon=ft.icons.Icons.DELETE,
                        icon_color="red",
                        tooltip="Eliminar",
                        on_click=lambda e, b=brand: self.confirm_delete(b.id)
                    ),
                ])
            ),
        ]

    def view_selected(self, brand):
        if not brand:
            return

        with get_db() as db:
            brand = brand_service.get(db, brand.id)
            if not brand:
                return

        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalles: {brand.name}"),
            content=ft.Column([
                ft.Text(f"ID: {brand.id}", weight="bold"),
                ft.Text(f"Nombre: {brand.name}"),
                ft.Text(f"Slug: {brand.slug}"),
                ft.Text(f"Descripción: {brand.description or 'N/A'}"),
                ft.Text(f"Activo: {'Sí' if brand.is_active else 'No'}"),
            ], tight=True),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=lambda _: self.page.pop_dialog(),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                )
            ]
        )
        self.page.show_dialog(dlg)

    def open_form_modal(self, e, brand_id=None):
        brand = None
        if brand_id:
            with get_db() as db:
                brand = brand_service.get(db, brand_id)

        txt_name = ft.TextField(
            label="Nombre (*)", width=300, autofocus=True,
            value=brand.name if brand else ""
        )
        txt_slug = ft.TextField(
            label="Slug (*)", width=300,
            hint_text="ej: mi-marca",
            value=brand.slug if brand else ""
        )
        txt_description = ft.TextField(
            label="Descripción", width=300, multiline=True, min_lines=2, max_lines=4,
            value=brand.description if brand else ""
        )

        def save_brand(e2):
            val_name = (txt_name.value or "").strip()
            val_slug = (txt_slug.value or "").strip()

            has_error = False
            if not val_name:
                txt_name.error_text = "El nombre es obligatorio"
                has_error = True
            if not val_slug:
                txt_slug.error_text = "El slug es obligatorio"
                has_error = True
            if has_error:
                self.update()
                return

            brand_data = {
                "name": val_name,
                "slug": val_slug,
                "description": (txt_description.value or "").strip() or None,
            }

            with get_db() as db:
                if brand_id:
                    db_brand = brand_service.get(db, brand_id)
                    brand_service.update(db, db_brand, brand_data)
                else:
                    brand_service.create(db, brand_data)

            self.page.pop_dialog()
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Editar Marca" if brand_id else "Nueva Marca"),
            content=ft.Column(
                [txt_name, txt_slug, txt_description],
                tight=True,
                spacing=15
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda _: self.page.pop_dialog(),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                ),
                ft.FilledButton(
                    "Guardar",
                    on_click=save_brand,
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color, color="white",
                        shape=ft.RoundedRectangleBorder(radius=5)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def confirm_delete(self, brand_id):
        def on_yes(e2):
            with get_db() as db:
                brand_service.soft_delete(db, brand_id)
            self.page.pop_dialog()
            self.selected_brand = None
            self.btn_view.disabled = True
            self.btn_delete.disabled = True
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro que deseas eliminar esta marca?"),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda _: self.page.pop_dialog(),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                ),
                ft.TextButton(
                    "Eliminar",
                    on_click=on_yes,
                    style=ft.ButtonStyle(color="red", shape=ft.RoundedRectangleBorder(radius=5))
                ),
            ]
        )
        self.page.show_dialog(dlg)
