import flet as ft
from services import client_service
from database.db import get_db
from ui.components.paginated_table import PaginatedTable


class ClientsView(ft.Container):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.expand = True
        self.padding = 30
        self.primary_color = "#2ecc71"
        self.selected_client = None
        
        # Evaluar Permisos
        self.is_admin = self.current_user.branch_id is None if self.current_user else True
        self.perms = self.current_user.permissions or {} if self.current_user else {}
        self.can_delete = self.is_admin or self.perms.get("can_delete_clients", False)
        self.can_edit = self.is_admin or self.perms.get("can_edit_clients", True) # Edit allowed by default for cashiers if not specified

        btn_shape = ft.RoundedRectangleBorder(radius=5)
        self.btn_add = ft.FilledButton(
            "➕ Agregar",
            on_click=self.open_form_modal,
            style=ft.ButtonStyle(bgcolor="#3498db", color="white", shape=btn_shape)
        )
        self.btn_delete = ft.ElevatedButton(
            "Eliminar Seleccionado",
            icon=ft.icons.Icons.DELETE_ROUNDED,
            on_click=lambda e: self.confirm_delete(self.selected_client.id),
            disabled=True,
            color="red",
            style=ft.ButtonStyle(shape=btn_shape),
            visible=self.can_delete
        )

        self.swt_show_inactive = ft.Switch(
            label="Mostrar inactivas",
            value=False,
            on_change=lambda e: self.table.refresh()
        )

        self.table = PaginatedTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Tipo Doc.")),
                ft.DataColumn(ft.Text("Nro. Documento")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            fetch_data_callback=self._fetch_clients,
            build_cells_callback=self._build_client_cells,
            on_row_click=self._on_row_selected,
            on_sort_callback=self._on_sort,
            on_row_double_click=self.view_selected,
            page_size=15
        )

        self.content = ft.Column(
            [
                ft.Text("👥 Administración de Clientes", size=28, weight="bold"),
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
        sort_map = {0: "name", 1: "document_type", 2: "document_number", 3: "phone", 4: "email", 5: "is_active"}
        self.current_order_by = sort_map.get(col_index)
        self.current_order_desc = not ascending
        self.table.refresh()

    def _fetch_clients(self, skip, limit):
        with get_db() as db:
            return client_service.get_all(
                db, 
                skip=skip, 
                limit=limit, 
                include_inactive=self.swt_show_inactive.value,
                order_by=getattr(self, 'current_order_by', None),
                order_desc=getattr(self, 'current_order_desc', False)
            )

    def _on_row_selected(self, client):
        self.selected_client = client
        has_selection = client is not None
        if self.can_delete:
            pass
        self.update()

    def _build_client_cells(self, client):
        return [
            ft.DataCell(ft.Text(client.name)),
            ft.DataCell(ft.Text(client.document_type)),
            ft.DataCell(ft.Text(str(client.document_number) if client.document_number else "-")),
            ft.DataCell(ft.Text(client.email or "-")),
            ft.DataCell(ft.Text(client.phone or "-")),
            ft.DataCell(
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.Icons.EDIT_ROUNDED,
                        icon_color="blue",
                        tooltip="Editar",
                        on_click=lambda e, c=client: self.open_form_modal(e, c.id),
                        visible=self.can_edit
                    ),
                    ft.IconButton(
                        icon=ft.icons.Icons.DELETE_ROUNDED,
                        icon_color="red",
                        tooltip="Eliminar",
                        on_click=lambda e, c=client: self.confirm_delete(c.id),
                        visible=self.can_delete
                    ),
                ])
            ),
        ]

    def view_selected(self, client):
        if not client:
            return

        with get_db() as db:
            client = client_service.get(db, client.id)
            if not client:
                return

        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalles del Cliente: {client.name}"),
            content=ft.Column([
                ft.Text(f"ID: {client.id}", weight="bold"),
                ft.Text(f"Nombre: {client.name}"),
                ft.Text(f"Documento: {client.document_type} {client.document_number}"),
                ft.Text(f"Email: {client.email or 'N/A'}"),
                ft.Text(f"Teléfono: {client.phone or 'N/A'}"),
                ft.Text(f"Dirección: {getattr(client, 'address', 'N/A')}"),
                ft.Text(f"Activo: {'Sí' if getattr(client, 'is_active', True) else 'No'}"),
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

    def open_form_modal(self, e, client_id=None):
        client = None
        if client_id:
            with get_db() as db:
                client = client_service.get(db, client_id)

        txt_name = ft.TextField(
            label="Nombre Completo (*)", width=300, autofocus=True,
            value=client.name if client else ""
        )
        dd_doc_type = ft.Dropdown(
            label="Tipo Doc.", width=150,
            options=[
                ft.dropdown.Option("DNI"),
                ft.dropdown.Option("CUIT"),
                ft.dropdown.Option("PASAPORTE")
            ],
            value=client.document_type if client else "DNI"
        )
        txt_doc_number = ft.TextField(
            label="Nro. Documento", width=150,
            value=str(client.document_number) if client and client.document_number else ""
        )
        txt_email = ft.TextField(label="Correo Electrónico", width=300, value=client.email if client else "")
        txt_phone = ft.TextField(label="Teléfono", width=300, value=client.phone if client else "")
        swt_active = ft.Switch(
            label="Activo", 
            value=getattr(client, 'is_active', True) if client else True
        )

        def save_client(e2):
            val_name = (txt_name.value or "").strip()
            if not val_name:
                txt_name.error_text = "El nombre es obligatorio"
                self.update()
                return

            client_data = {
                "name": val_name,
                "document_type": dd_doc_type.value,
                "document_number": (txt_doc_number.value or "").strip() or None,
                "email": (txt_email.value or "").strip() or None,
                "phone": (txt_phone.value or "").strip() or None,
                "is_active": swt_active.value,
            }

            with get_db() as db:
                if client_id:
                    db_client = client_service.get(db, client_id)
                    client_service.update(db, db_client, client_data)
                else:
                    client_service.create(db, client_data)

            self.page.pop_dialog()
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Editar Cliente" if client_id else "Nuevo Cliente"),
            content=ft.Column(
                [
                    txt_name,
                    ft.Row([dd_doc_type, txt_doc_number]),
                    txt_email,
                    txt_phone,
                    swt_active,
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
                    on_click=save_client,
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color, color="white",
                        shape=ft.RoundedRectangleBorder(radius=5)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def confirm_delete(self, client_id):
        def on_yes(e2):
            with get_db() as db:
                client_service.soft_delete(db, client_id)
            self.page.pop_dialog()
            self.selected_client = None
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro que deseas eliminar este cliente?"),
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
