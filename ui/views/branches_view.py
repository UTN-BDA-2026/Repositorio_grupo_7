import flet as ft
from services.branch_service import branch_service
from database.db import get_db
from ui.components.paginated_table import PaginatedTable


class BranchesView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        self.primary_color = "#34495e"
        self.selected_branch = None

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
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Código de Activación")),
                ft.DataColumn(ft.Text("Activo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            fetch_data_callback=self._fetch_branches,
            build_cells_callback=self._build_branch_cells,
            on_row_click=self._on_row_selected,
            on_row_double_click=self.view_selected,
            on_sort_callback=self._on_sort,
            page_size=15
        )

        self.content = ft.Column(
            [
                ft.Text("🏪 Administración de Sucursales", size=28, weight="bold"),
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
        sort_map = {0: "name", 1: "code", 2: "location", 3: "is_active"}
        self.current_order_by = sort_map.get(col_index)
        self.current_order_desc = not ascending
        self.table.refresh()

    def _fetch_branches(self, skip, limit):
        with get_db() as db:
            return branch_service.get_all(
                db, 
                skip=skip, 
                limit=limit, 
                include_inactive=self.swt_show_inactive.value,
                order_by=getattr(self, 'current_order_by', None),
                order_desc=getattr(self, 'current_order_desc', False)
            )

    def _on_row_selected(self, branch):
        self.selected_branch = branch
        self.update()

    def _build_branch_cells(self, branch):
        return [
            ft.DataCell(ft.Text(branch.name)),
            ft.DataCell(ft.Text(branch.address or "-")),
            ft.DataCell(ft.Text(branch.phone or "-")),
            ft.DataCell(ft.Text(branch.activation_code or "-")),
            ft.DataCell(ft.Text("Sí" if branch.is_active else "No")),
            ft.DataCell(
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.Icons.EDIT,
                        icon_color="blue",
                        tooltip="Editar",
                        on_click=lambda e, b=branch: self.open_form_modal(e, b.id)
                    ),
                    ft.IconButton(
                        icon=ft.icons.Icons.DELETE,
                        icon_color="red",
                        tooltip="Eliminar",
                        on_click=lambda e, b=branch: self.confirm_delete(b.id)
                    ),
                ])
            ),
        ]

    def view_selected(self, branch):
        if not branch:
            return

        with get_db() as db:
            branch = branch_service.get(db, branch.id)
            if not branch:
                return

        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalles: {branch.name}"),
            content=ft.Column([
                ft.Text(f"ID: {branch.id}", weight="bold"),
                ft.Text(f"Nombre: {branch.name}"),
                ft.Text(f"Dirección: {branch.address or 'N/A'}"),
                ft.Text(f"Teléfono: {branch.phone or 'N/A'}"),
                ft.Text(f"Código: {branch.activation_code or 'N/A'}"),
                ft.Text(f"Activo: {'Sí' if branch.is_active else 'No'}"),
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

    def open_form_modal(self, e, branch_id=None):
        branch = None
        if branch_id:
            with get_db() as db:
                branch = branch_service.get(db, branch_id)

        txt_name = ft.TextField(
            label="Nombre (*)", width=300, autofocus=True,
            value=branch.name if branch else ""
        )
        txt_address = ft.TextField(
            label="Dirección", width=300,
            value=branch.address if branch else ""
        )
        txt_phone = ft.TextField(
            label="Teléfono", width=300,
            value=branch.phone if branch else ""
        )
        txt_code = ft.TextField(
            label="Código de Activación", width=300,
            value=branch.activation_code if branch else ""
        )
        swt_active = ft.Switch(
            label="Sucursal Activa", 
            value=branch.is_active if branch else True
        )

        def save_branch(e2):
            val_name = (txt_name.value or "").strip()

            has_error = False
            if not val_name:
                txt_name.error_text = "El nombre es obligatorio"
                has_error = True
            if has_error:
                self.update()
                return

            branch_data = {
                "name": val_name,
                "address": (txt_address.value or "").strip() or None,
                "phone": (txt_phone.value or "").strip() or None,
                "activation_code": (txt_code.value or "").strip() or None,
                "is_active": swt_active.value,
            }

            with get_db() as db:
                if branch_id:
                    db_branch = branch_service.get(db, branch_id)
                    branch_service.update(db, db_branch, branch_data)
                else:
                    branch_service.create(db, branch_data)

            self.page.pop_dialog()
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Editar Sucursal" if branch_id else "Nueva Sucursal"),
            content=ft.Column(
                [txt_name, txt_address, txt_phone, txt_code, swt_active],
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
                    on_click=save_branch,
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color, color="white",
                        shape=ft.RoundedRectangleBorder(radius=5)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def confirm_delete(self, branch_id):
        def on_yes(e2):
            with get_db() as db:
                branch_service.soft_delete(db, branch_id)
            self.page.pop_dialog()
            self.selected_branch = None
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro que deseas eliminar esta sucursal?"),
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
