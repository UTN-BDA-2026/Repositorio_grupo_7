import flet as ft
from services.tax_service import tax_service
from database.db import get_db
from ui.components.paginated_table import PaginatedTable


class TaxesView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        self.primary_color = "#6200ee"
        self.selected_tax = None

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
                ft.DataColumn(ft.Text("Tasa (%)"), numeric=True),
                ft.DataColumn(ft.Text("Por Defecto")),
                ft.DataColumn(ft.Text("Activo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            fetch_data_callback=self._fetch_taxes,
            build_cells_callback=self._build_tax_cells,
            on_row_click=self._on_row_selected,
            on_sort_callback=self._on_sort,
            on_row_double_click=self.view_selected,
            page_size=15
        )

        self.content = ft.Column(
            [
                ft.Text("💲 Administración de Impuestos", size=28, weight="bold"),
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
        sort_map = {0: "name", 1: "rate", 2: "is_default", 3: "is_active"}
        self.current_order_by = sort_map.get(col_index)
        self.current_order_desc = not ascending
        self.table.refresh()

    def _fetch_taxes(self, skip, limit):
        with get_db() as db:
            return tax_service.get_all(
                db, 
                skip=skip, 
                limit=limit, 
                include_inactive=self.swt_show_inactive.value,
                order_by=getattr(self, 'current_order_by', None),
                order_desc=getattr(self, 'current_order_desc', False)
            )

    def _on_row_selected(self, tax):
        self.selected_tax = tax
        has_selection = tax is not None
        self.update()

    def _build_tax_cells(self, tax):
        return [
            ft.DataCell(ft.Text(tax.name)),
            ft.DataCell(ft.Text(f"{tax.rate}%")),
            ft.DataCell(ft.Text("Sí" if tax.is_default else "No")),
            ft.DataCell(ft.Text("Sí" if tax.is_active else "No")),
            ft.DataCell(
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.Icons.EDIT,
                        icon_color="blue",
                        tooltip="Editar",
                        on_click=lambda e, t=tax: self.open_form_modal(e, t.id)
                    ),
                    ft.IconButton(
                        icon=ft.icons.Icons.DELETE,
                        icon_color="red",
                        tooltip="Eliminar",
                        on_click=lambda e, t=tax: self.confirm_delete(t.id)
                    ),
                ])
            ),
        ]

    def view_selected(self, tax):
        if not tax:
            return

        with get_db() as db:
            tax = tax_service.get(db, tax.id)
            if not tax:
                return

        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalles: {tax.name}"),
            content=ft.Column([
                ft.Text(f"ID: {tax.id}", weight="bold"),
                ft.Text(f"Nombre: {tax.name}"),
                ft.Text(f"Tasa: {tax.rate}%"),
                ft.Text(f"Por Defecto: {'Sí' if tax.is_default else 'No'}"),
                ft.Text(f"Activo: {'Sí' if tax.is_active else 'No'}"),
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

    def open_form_modal(self, e, tax_id=None):
        tax = None
        if tax_id:
            with get_db() as db:
                tax = tax_service.get(db, tax_id)

        txt_name = ft.TextField(
            label="Nombre (*)", width=300, autofocus=True,
            value=tax.name if tax else ""
        )
        txt_rate = ft.TextField(
            label="Tasa (*)", width=150,
            hint_text="ej: 21.00",
            suffix=ft.Text("%"),
            value=str(tax.rate) if tax else ""
        )
        chk_default = ft.Checkbox(
            label="Impuesto por defecto",
            value=tax.is_default if tax else False
        )
        swt_active = ft.Switch(
            label="Activo", 
            value=tax.is_active if tax else True
        )

        def save_tax(e2):
            val_name = (txt_name.value or "").strip()
            val_rate = (txt_rate.value or "").strip()

            has_error = False
            if not val_name:
                txt_name.error_text = "El nombre es obligatorio"
                has_error = True
            if not val_rate:
                txt_rate.error_text = "La tasa es obligatoria"
                has_error = True
            if has_error:
                self.update()
                return

            try:
                rate = float(val_rate)
            except ValueError:
                txt_rate.error_text = "Tasa inválida"
                self.update()
                return

            tax_data = {
                "name": val_name,
                "rate": rate,
                "is_default": chk_default.value or False,
                "is_active": swt_active.value,
            }

            with get_db() as db:
                if tax_id:
                    db_tax = tax_service.get(db, tax_id)
                    tax_service.update(db, db_tax, tax_data)
                else:
                    tax_service.create(db, tax_data)

            self.page.pop_dialog()
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Editar Impuesto" if tax_id else "Nuevo Impuesto"),
            content=ft.Column(
                [txt_name, txt_rate, chk_default, swt_active],
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
                    on_click=save_tax,
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color, color="white",
                        shape=ft.RoundedRectangleBorder(radius=5)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def confirm_delete(self, tax_id):
        def on_yes(e2):
            with get_db() as db:
                tax_service.soft_delete(db, tax_id)
            self.page.pop_dialog()
            self.selected_tax = None
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro que deseas eliminar este impuesto?"),
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
