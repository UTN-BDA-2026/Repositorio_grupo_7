import flet as ft
from services.user_service import user_service
from services.branch_service import branch_service
from database.db import get_db
from flet_ui.components.paginated_table import PaginatedTable


class UsersView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        self.primary_color = "#9b59b6" # A distinct color for Users
        self.selected_user = None

        btn_shape = ft.RoundedRectangleBorder(radius=5)
        self.btn_add = ft.FilledButton(
            "Agregar",
            icon=ft.icons.Icons.ADD_ROUNDED,
            on_click=self.open_form_modal,
            style=ft.ButtonStyle(bgcolor=self.primary_color, color="white", shape=btn_shape)
        )
        self.btn_view = ft.ElevatedButton(
            "Ver Seleccionado",
            icon=ft.icons.Icons.VISIBILITY_ROUNDED,
            on_click=lambda e: self.view_selected(self.selected_user),
            disabled=True,
            style=ft.ButtonStyle(shape=btn_shape)
        )
        self.btn_delete = ft.ElevatedButton(
            "Eliminar Seleccionado",
            icon=ft.icons.Icons.DELETE_ROUNDED,
            on_click=lambda e: self.confirm_delete(self.selected_user.id),
            disabled=True,
            color="red",
            style=ft.ButtonStyle(shape=btn_shape)
        )

        self.table = PaginatedTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Sucursal")),
                ft.DataColumn(ft.Text("PIN Caja")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            fetch_data_callback=self._fetch_users,
            build_cells_callback=self._build_user_cells,
            on_row_click=self._on_row_selected,
            on_row_double_click=self.view_selected,
            page_size=15
        )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.icons.Icons.PEOPLE_ROUNDED, size=28, color=self.primary_color),
                        ft.Text("Administración de Usuarios", size=28, weight="bold"),
                    ],
                    spacing=10
                ),
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

    def _fetch_users(self, skip, limit):
        with get_db() as db:
            return user_service.get_all(db, skip=skip, limit=limit)

    def _on_row_selected(self, user):
        self.selected_user = user
        has_selection = user is not None
        self.btn_view.disabled = not has_selection
        self.btn_delete.disabled = not has_selection
        self.update()

    def _build_user_cells(self, user):
        return [
            ft.DataCell(ft.Text(user.name)),
            ft.DataCell(ft.Text(user.email)),
            ft.DataCell(ft.Text(str(user.branch_id) if user.branch_id else "Todas (Admin)")),
            ft.DataCell(ft.Text(user.pos_pin or "-")),
            ft.DataCell(
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.Icons.EDIT_ROUNDED,
                        icon_color="blue",
                        tooltip="Editar",
                        on_click=lambda e, u=user: self.open_form_modal(e, u.id)
                    ),
                    ft.IconButton(
                        icon=ft.icons.Icons.DELETE_ROUNDED,
                        icon_color="red",
                        tooltip="Eliminar",
                        on_click=lambda e, u=user: self.confirm_delete(u.id)
                    ),
                ])
            ),
        ]

    def view_selected(self, user):
        if not user:
            return

        with get_db() as db:
            user = user_service.get(db, user.id)
            if not user:
                return
            branch = branch_service.get(db, user.branch_id) if user.branch_id else None

        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalles del Usuario: {user.name}"),
            content=ft.Column([
                ft.Text(f"ID: {user.id}", weight="bold"),
                ft.Text(f"Nombre: {user.name}"),
                ft.Text(f"Email: {user.email}"),
                ft.Text(f"Sucursal Asignada: {branch.name if branch else 'Todas (Sin asignar)'}"),
                ft.Text(f"PIN Caja: {user.pos_pin or 'N/A'}"),
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

    def open_form_modal(self, e, user_id=None):
        user = None
        branches = []
        with get_db() as db:
            if user_id:
                user = user_service.get(db, user_id)
            branches = branch_service.get_all(db, limit=100)

        txt_name = ft.TextField(
            label="Nombre Completo (*)", width=300, autofocus=True,
            value=user.name if user else ""
        )
        txt_email = ft.TextField(
            label="Correo Electrónico (*)", width=300,
            value=user.email if user else ""
        )
        txt_password = ft.TextField(
            label="Contraseña" + (" (Dejar en blanco para no cambiar)" if user else " (*)"), 
            width=300, password=True, can_reveal_password=True
        )
        txt_pos_pin = ft.TextField(
            label="PIN Caja (4-6 dígitos)", width=300,
            value=user.pos_pin if user else "",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        branch_options = [ft.dropdown.Option(key="", text="Ninguna / Administrador Global")]
        for b in branches:
            branch_options.append(ft.dropdown.Option(key=str(b.id), text=b.name))
            
        dd_branch = ft.Dropdown(
            label="Sucursal Asignada", width=300,
            options=branch_options,
            value=str(user.branch_id) if user and user.branch_id else ""
        )

        def save_user(e2):
            val_name = (txt_name.value or "").strip()
            val_email = (txt_email.value or "").strip()
            val_pass = (txt_password.value or "").strip()
            
            if not val_name:
                txt_name.error_text = "El nombre es obligatorio"
                self.update()
                return
            if not val_email:
                txt_email.error_text = "El email es obligatorio"
                self.update()
                return
            if not user_id and not val_pass:
                txt_password.error_text = "La contraseña es obligatoria para nuevos usuarios"
                self.update()
                return

            user_data = {
                "name": val_name,
                "email": val_email,
                "branch_id": dd_branch.value if dd_branch.value else None,
                "pos_pin": (txt_pos_pin.value or "").strip() or None,
            }
            if val_pass:
                user_data["password"] = val_pass

            try:
                with get_db() as db:
                    if user_id:
                        db_user = user_service.get(db, user_id)
                        user_service.update(db, db_user, user_data)
                    else:
                        user_service.create(db, user_data)
                
                self.page.pop_dialog()
                self.table.refresh()
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
                self.page.snack_bar.open = True
                self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Editar Usuario" if user_id else "Nuevo Usuario"),
            content=ft.Column(
                [
                    txt_name,
                    txt_email,
                    txt_password,
                    txt_pos_pin,
                    dd_branch
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
                    on_click=save_user,
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color, color="white",
                        shape=ft.RoundedRectangleBorder(radius=5)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def confirm_delete(self, user_id):
        def on_yes(e2):
            with get_db() as db:
                user_service.soft_delete(db, user_id)
            self.page.pop_dialog()
            self.selected_user = None
            self.btn_view.disabled = True
            self.btn_delete.disabled = True
            self.table.refresh()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro que deseas eliminar este usuario?"),
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
