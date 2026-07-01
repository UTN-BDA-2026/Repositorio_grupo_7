import flet as ft
from services.supplier_service import supplier_service
from database.db import get_db
from ui.components.paginated_table import PaginatedTable


class SuppliersView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        self.primary_color = "#e74c3c"
        self.selected_supplier = None

        btn_shape = ft.RoundedRectangleBorder(radius=5)
        self.btn_add = ft.FilledButton(
            "Agregar",
            icon=ft.icons.Icons.ADD_ROUNDED,
            on_click=self.open_form_modal,
            style=ft.ButtonStyle(bgcolor="#3498db", color="white", shape=btn_shape)
        )

        self.table = PaginatedTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("CUIT/NIT")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            fetch_data_callback=self._fetch_suppliers,
            build_cells_callback=self._build_supplier_cells,
            on_row_click=self._on_row_selected,
            on_row_double_click=self.view_selected,
            page_size=15
        )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.icons.Icons.LOCAL_SHIPPING_ROUNDED, size=28, color=self.primary_color),
                        ft.Text("Administración de Proveedores", size=28, weight="bold"),
                    ],
                    spacing=10
                ),
                ft.Row(
                    [self.btn_add],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10
                ),
                ft.Divider(height=5, color="transparent"),
                self.table,
            ],
            expand=True
        )

    def _fetch_suppliers(self, skip, limit):
        with get_db() as db:
            return supplier_service.get_all(db, skip=skip, limit=limit)

    def _on_row_selected(self, supplier):
        self.selected_supplier = supplier
        has_selection = supplier is not None
        self.update()

    def _build_supplier_cells(self, supplier):
        return [
            ft.DataCell(ft.Text(supplier.name)),
            ft.DataCell(ft.Text(supplier.tax_id or "-")),
            ft.DataCell(ft.Text(supplier.email or "-")),
            ft.DataCell(ft.Text(supplier.phone or "-")),
            ft.DataCell(
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.Icons.EDIT_ROUNDED,
                        icon_color="blue",
                        tooltip="Editar",
                        on_click=lambda e, s=supplier: self.open_form_modal(e, s.id)
                    ),
                    ft.IconButton(
                        icon=ft.icons.Icons.DELETE_ROUNDED,
                        icon_color="red",
                        tooltip="Eliminar",
                        on_click=lambda e, s=supplier: self.confirm_delete(s.id)
                    ),
                ])
            ),
        ]

    def view_selected(self, supplier):
        if not supplier:
            return

        with get_db() as db:
            supplier = supplier_service.get(db, supplier.id)
            if not supplier:
                return

        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalles del Proveedor: {supplier.name}"),
            content=ft.Column([
                ft.Text(f"ID: {supplier.id}", weight="bold"),
                ft.Text(f"Nombre: {supplier.name}"),
                ft.Text(f"CUIT/NIT (Tax ID): {supplier.tax_id or 'N/A'}"),
                ft.Text(f"Email: {supplier.email or 'N/A'}"),
                ft.Text(f"Teléfono: {supplier.phone or 'N/A'}"),
                ft.Text(f"Dirección: {supplier.address or 'N/A'}"),
                ft.Text(f"Activo: {'Sí' if getattr(supplier, 'is_active', True) else 'No'}"),
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

    def open_form_modal(self, e, supplier_id=None):
        supplier = None
        if supplier_id:
            with get_db() as db:
                supplier = supplier_service.get(db, supplier_id)

        txt_name = ft.TextField(
            label="Nombre o Razón Social (*)", width=300, autofocus=True,
            value=supplier.name if supplier else ""
        )
        txt_tax_id = ft.TextField(
            label="CUIT/NIT", width=300,
            value=supplier.tax_id if supplier else ""
        )
        txt_email = ft.TextField(label="Correo Electrónico", width=300, value=supplier.email if supplier else "")
        txt_phone = ft.TextField(label="Teléfono", width=300, value=supplier.phone if supplier else "")
        txt_address = ft.TextField(label="Dirección", width=300, multiline=True, min_lines=2, max_lines=4, value=supplier.address if supplier else "")

        def save_supplier(e2):
            val_name = (txt_name.value or "").strip()
            if not val_name:
                txt_name.error_text = "El nombre es obligatorio"
                self.update()
                return

            supplier_data = {
                "name": val_name,
                "tax_id": (txt_tax_id.value or "").strip() or None,
                "email": (txt_email.value or "").strip() or None,
                "phone": (txt_phone.value or "").strip() or None,
                "address": (txt_address.value or "").strip() or None,
            }

            try:
                with get_db() as db:
                    if supplier_id:
                        db_supplier = supplier_service.get(db, supplier_id)
                        supplier_service.update(db, db_supplier, supplier_data)
                    else:
                        supplier_service.create(db, supplier_data)
                
                self.page.pop_dialog()
                self.table.refresh()
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
                self.page.snack_bar.open = True
                self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Editar Proveedor" if supplier_id else "Nuevo Proveedor"),
            content=ft.Column(
                [
                    txt_name,
                    txt_tax_id,
                    txt_email,
                    txt_phone,
                    txt_address,
                ],
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
                    on_click=save_supplier,
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color, color="white",
                        shape=ft.RoundedRectangleBorder(radius=5)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def confirm_delete(self, supplier_id):
        def on_yes(e2):
            with get_db() as db:
                supplier_service.soft_delete(db, supplier_id)
            self.page.pop_dialog()
            self.selected_supplier = None
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro que deseas eliminar este proveedor?"),
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
