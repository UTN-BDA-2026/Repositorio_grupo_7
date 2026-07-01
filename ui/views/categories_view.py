import flet as ft
from services.category_service import category_service
from database.db import get_db
from ui.components.paginated_table import PaginatedTable


class CategoriesView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        self.primary_color = "#6200ee"
        self.selected_category = None

        btn_shape = ft.RoundedRectangleBorder(radius=5)
        self.btn_add = ft.FilledButton(
            "➕ Agregar",
            on_click=self.open_form_modal,
            style=ft.ButtonStyle(bgcolor="#3498db", color="white", shape=btn_shape)
        )

        self.swt_show_inactive = ft.Switch(
            label="Mostrar inactivas",
            value=False,
            on_change=lambda e: self.table.refresh()
        )

        self.table = PaginatedTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Activo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            fetch_data_callback=self._fetch_categories,
            build_cells_callback=self._build_category_cells,
            on_row_click=self._on_row_selected,
            on_row_double_click=self.view_selected,
            page_size=15
        )

        self.content = ft.Column(
            [
                ft.Text("🗂 Administración de Categorías", size=28, weight="bold"),
                ft.Row(
                    [self.swt_show_inactive, self.btn_add],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=20
                ),
                ft.Divider(height=5, color="transparent"),
                self.table,
            ],
            expand=True
        )

    def _on_sort(self, col_index, ascending):
        sort_map = {0: "name", 1: "description", 2: "is_active"}
        self.current_order_by = sort_map.get(col_index)
        self.current_order_desc = not ascending
        self.table.refresh()

    def _fetch_categories(self, skip, limit):
        with get_db() as db:
            return category_service.get_all(
                db, 
                skip=skip, 
                limit=limit, 
                include_inactive=self.swt_show_inactive.value,
                order_by=getattr(self, 'current_order_by', None),
                order_desc=getattr(self, 'current_order_desc', False)
            )

    def _on_row_selected(self, category):
        self.selected_category = category
        has_selection = category is not None
        self.update()

    def _build_category_cells(self, category):
        return [
            ft.DataCell(ft.Text(category.name)),
            ft.DataCell(ft.Text(category.description or "-")),
            ft.DataCell(ft.Text("Sí" if category.is_active else "No")),
            ft.DataCell(
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.Icons.EDIT,
                        icon_color="blue",
                        tooltip="Editar",
                        on_click=lambda e, c=category: self.open_form_modal(e, c.id)
                    ),
                    ft.IconButton(
                        icon=ft.icons.Icons.DELETE,
                        icon_color="red",
                        tooltip="Eliminar",
                        on_click=lambda e, c=category: self.confirm_delete(c.id)
                    ),
                ])
            ),
        ]

    def view_selected(self, category):
        if not category:
            return

        with get_db() as db:
            category = category_service.get(db, category.id)
            if not category:
                return

        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalles: {category.name}"),
            content=ft.Column([
                ft.Text(f"ID: {category.id}", weight="bold"),
                ft.Text(f"Nombre: {category.name}"),
                ft.Text(f"Descripción: {category.description or 'N/A'}"),
                ft.Text(f"Activo: {'Sí' if category.is_active else 'No'}"),
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

    def open_form_modal(self, e, category_id=None):
        category = None
        if category_id:
            with get_db() as db:
                category = category_service.get(db, category_id)

        txt_name = ft.TextField(
            label="Nombre (*)", width=300, autofocus=True,
            value=category.name if category else ""
        )
        txt_description = ft.TextField(
            label="Descripción", width=300, multiline=True, min_lines=2, max_lines=4,
            value=category.description if category else ""
        )
        swt_active = ft.Switch(
            label="Activa", 
            value=category.is_active if category else True
        )

        def save_category(e2):
            val_name = (txt_name.value or "").strip()
            if not val_name:
                txt_name.error_text = "El nombre es obligatorio"
                self.update()
                return

            category_data = {
                "name": val_name,
                "description": (txt_description.value or "").strip() or None,
                "is_active": swt_active.value,
            }

            with get_db() as db:
                if category_id:
                    db_category = category_service.get(db, category_id)
                    category_service.update(db, db_category, category_data)
                else:
                    category_service.create(db, category_data)

            self.page.pop_dialog()
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Editar Categoría" if category_id else "Nueva Categoría"),
            content=ft.Column(
                [txt_name, txt_description, swt_active],
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
                    on_click=save_category,
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color, color="white",
                        shape=ft.RoundedRectangleBorder(radius=5)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def confirm_delete(self, category_id):
        def on_yes(e2):
            with get_db() as db:
                category_service.soft_delete(db, category_id)
            self.page.pop_dialog()
            self.selected_category = None
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro que deseas eliminar esta categoría?"),
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
