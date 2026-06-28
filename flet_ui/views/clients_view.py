import flet as ft
from services import client_service
from database.db import get_db

class ClientsView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        
        self.primary_color = "#6200ee"
        
        from flet_ui.components.paginated_table import PaginatedTable
        
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
            build_row_callback=self._build_client_row,
            page_size=15
        )
        
        # Botones de acción global
        btn_shape = ft.RoundedRectangleBorder(radius=5)
        self.btn_add = ft.FilledButton("➕ Agregar", on_click=self.open_form_modal, style=ft.ButtonStyle(bgcolor=self.primary_color, color="white", shape=btn_shape))
        self.btn_view = ft.ElevatedButton("👁 Ver Seleccionado", on_click=self.view_selected, disabled=True, style=ft.ButtonStyle(shape=btn_shape))
        self.btn_delete = ft.ElevatedButton("🗑 Eliminar Seleccionado", on_click=self.delete_selected, disabled=True, color="red", style=ft.ButtonStyle(shape=btn_shape))
        
        self.selected_item_id = None
        
        self.content = ft.Column(
            [
                ft.Text("👥 Administración de Clientes", size=28, weight="bold"),
                ft.Row(
                    [
                        self.btn_add,
                        self.btn_view,
                        self.btn_delete,
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10
                ),
                ft.Divider(height=5, color="transparent"),
                self.table, # Insertamos la PaginatedTable
            ],
            expand=True
        )

    def _fetch_clients(self, skip, limit):
        with get_db() as db:
            return client_service.get_all(db, skip=skip, limit=limit)

    def handle_row_select(self, e, client_id):
        if e.control.selected:
            self.selected_item_id = client_id
            # Desmarcar otras filas
            for row in self.table.table.rows:
                if row.data != client_id:
                    row.selected = False
            self.btn_view.disabled = False
            self.btn_delete.disabled = False
        else:
            self.selected_item_id = None
            self.btn_view.disabled = True
            self.btn_delete.disabled = True
            
        self.update()

    def handle_double_tap(self, e, client_id):
        # Seleccionar automáticamente y abrir vista
        self.selected_item_id = client_id
        for row in self.table.table.rows:
            row.selected = (row.data == client_id)
        self.btn_view.disabled = False
        self.btn_delete.disabled = False
        self.update()
        self.view_selected(e)

    def _build_client_row(self, client):
        def on_dbl_click(e):
            self.handle_double_tap(e, client.id)
            
        return ft.DataRow(
            data=client.id,
            on_select_change=lambda e: self.handle_row_select(e, client.id),
            selected=(self.selected_item_id == client.id),
            cells=[
                ft.DataCell(ft.Text(client.name), on_double_tap=on_dbl_click),
                ft.DataCell(ft.Text(client.document_type), on_double_tap=on_dbl_click),
                ft.DataCell(ft.Text(str(client.document_number) if client.document_number else "-"), on_double_tap=on_dbl_click),
                ft.DataCell(ft.Text(client.email or "-"), on_double_tap=on_dbl_click),
                ft.DataCell(ft.Text(client.phone or "-"), on_double_tap=on_dbl_click),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(icon=ft.icons.Icons.EDIT, icon_color="blue", tooltip="Editar", on_click=lambda e: self.open_form_modal(e, client.id)),
                        ft.IconButton(icon=ft.icons.Icons.DELETE, icon_color="red", tooltip="Eliminar", on_click=lambda e: self.confirm_delete(client.id))
                    ])
                ),
            ]
        )

    def open_form_modal(self, e, client_id=None):
        client = None
        if client_id:
            with get_db() as db:
                client = client_service.get(db, client_id)

        # Campos del formulario
        txt_name = ft.TextField(label="Nombre Completo (*)", width=300, autofocus=True, value=client.name if client else "")
        dd_doc_type = ft.Dropdown(
            label="Tipo Doc.",
            width=150,
            options=[ft.dropdown.Option("DNI"), ft.dropdown.Option("CUIT"), ft.dropdown.Option("PASAPORTE")],
            value=client.document_type if client else "DNI"
        )
        txt_doc_number = ft.TextField(label="Nro. Documento", width=150, value=str(client.document_number) if client and client.document_number else "")
        txt_email = ft.TextField(label="Correo Electrónico", width=300, value=client.email if client else "")
        txt_phone = ft.TextField(label="Teléfono", width=300, value=client.phone if client else "")
        
        # Validar y guardar
        def save_client(e2):
            val_name = (txt_name.value or "").strip()
            val_doc_num = (txt_doc_number.value or "").strip()
            val_email = (txt_email.value or "").strip()
            val_phone = (txt_phone.value or "").strip()
            
            if not val_name:
                txt_name.error_text = "El nombre es obligatorio"
                self.update()
                return
            
            client_data = {
                "name": val_name,
                "document_type": dd_doc_type.value,
                "document_number": val_doc_num or None,
                "email": val_email or None,
                "phone": val_phone or None,
            }
            
            with get_db() as db:
                if client_id:
                    db_client = client_service.get(db, client_id)
                    client_service.update(db, db_client, client_data)
                else:
                    client_service.create(db, client_data)
            
            self.page.pop_dialog()
            self.table.refresh() # Recargar la tabla automáticamente
            
        def close_dlg(dialog):
            self.page.pop_dialog()

        dlg = ft.AlertDialog(
            title=ft.Text("Editar Cliente" if client_id else "Nuevo Cliente"),
            content=ft.Column(
                [
                    txt_name,
                    ft.Row([dd_doc_type, txt_doc_number]),
                    txt_email,
                    txt_phone
                ],
                tight=True,
                spacing=15
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dlg(dlg), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))),
                ft.FilledButton("Guardar", on_click=save_client, style=ft.ButtonStyle(bgcolor=self.primary_color, color="white", shape=ft.RoundedRectangleBorder(radius=5))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.show_dialog(dlg)

    def view_selected(self, e):
        if not self.selected_item_id:
            return
            
        with get_db() as db:
            client = client_service.get(db, self.selected_item_id)
            if not client:
                return

        def close_dlg(page, dialog):
            dialog.open = False
            page.update()

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
                ft.TextButton("Cerrar", on_click=lambda e: close_dlg(e.control.page, e.control.parent.parent), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)))
            ]
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def delete_selected(self, e):
        if self.selected_item_id:
            self.confirm_delete(self.selected_item_id)

    def confirm_delete(self, client_id):
        def on_yes(e2):
            with get_db() as db:
                client_service.soft_delete(db, client_id)
            self.page.pop_dialog()
            self.table.refresh()
            
        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro que deseas eliminar este cliente?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dlg(dlg), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))),
                ft.TextButton("Eliminar", on_click=on_yes, style=ft.ButtonStyle(color="red", shape=ft.RoundedRectangleBorder(radius=5))),
            ]
        )
        
        def close_dlg(d):
            self.page.pop_dialog()

        self.page.show_dialog(dlg)
