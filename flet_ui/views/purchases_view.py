import flet as ft
from database.db import get_db
from database.transactions import process_purchase_transaction
from services.supplier_service import supplier_service
from services.product_service import product_service

ACCENT = "#3498db"
SUCCESS = "#27ae60"
PRIMARY = "#007bff"
DANGER = "#dc3545"
CARD_RADIUS = 10

class PurchasesView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30

        self.suppliers = []
        self.products = []
        self.cart_items = []
        
        # Modal state
        self._selected_supplier_id = None
        self._selected_supplier_name = "Seleccione un Proveedor"

        # Right column state
        self.last_product = None

        with get_db() as db:
            self.suppliers = supplier_service.get_all(db, limit=1000)
            self.products = product_service.get_all(db, limit=1000)

        # Buscador en tiempo real (Igual a POS)
        self.txt_search = ft.TextField(
            hint_text="Buscar producto por nombre, cód o SKU...",
            height=45,
            content_padding=10,
            text_size=14,
            border=ft.InputBorder.UNDERLINE,
            expand=True,
            on_change=self.handle_search,
        )
        self.search_results = ft.ListView(
            height=250,
            spacing=0,
        )

        section_search = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.Icons.SEARCH_ROUNDED, size=20, color=ACCENT),
                            ft.Text("Buscador de Productos a Ingresar", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, weight="bold"),
                        ],
                        spacing=8,
                    ),
                    ft.Row([self.txt_search]),
                ],
                spacing=10,
            ),
            bgcolor="surfacevariant",
            border_radius=CARD_RADIUS,
            padding=20,
        )

        # Tabla del carrito (Columna Izquierda)
        self.cart_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Cant."), numeric=True),
                ft.DataColumn(ft.Text("Costo Unit."), numeric=True),
                ft.DataColumn(ft.Text("Subtotal"), numeric=True),
                ft.DataColumn(ft.Text("")),
            ],
            rows=[],
            heading_row_color="surfacevariant",
            expand=True,
            data_row_min_height=55,
            data_row_max_height=65,
        )

        self.lbl_empty_cart = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.icons.Icons.INVENTORY_2_OUTLINED, size=48, color="grey"),
                    ft.Text("No hay productos para ingresar", size=16, color="grey"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

        self.cart_content = ft.Column([self.lbl_empty_cart], expand=True, scroll=ft.ScrollMode.AUTO)

        section_cart = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.Icons.FORMAT_LIST_BULLETED_ROUNDED, size=20, color=ACCENT),
                            ft.Text("Detalle de la Compra", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, weight="bold"),
                        ],
                        spacing=8,
                    ),
                    self.cart_content,
                ],
                expand=True,
            ),
            bgcolor="surfacevariant",
            border_radius=CARD_RADIUS,
            padding=20,
            expand=True
        )

        left_layout = ft.Container(
            content=ft.Column([section_search, section_cart], spacing=15),
            top=0, bottom=0, left=0, right=0
        )

        self.search_results_container = ft.Container(
            content=self.search_results,
            bgcolor="white",
            border_radius=8,
            border=ft.Border(
                top=ft.BorderSide(1, "black12"),
                bottom=ft.BorderSide(1, "black12"),
                left=ft.BorderSide(1, "black12"),
                right=ft.BorderSide(1, "black12")
            ),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color="black26"),
            top=125,
            left=20,
            right=20,
            visible=False
        )

        left_column = ft.Stack([left_layout, self.search_results_container], expand=7)

        # --- COLUMNA DERECHA ---
        
        # Detalle de último producto
        self.lbl_last_prod_name = ft.Text("Ningún producto", theme_style=ft.TextThemeStyle.TITLE_LARGE, weight="bold", color=PRIMARY)
        self.lbl_last_prod_price = ft.Text("$ 0.00", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, color="grey")
        self.lbl_last_prod_sku = ft.Text("SKU: -", theme_style=ft.TextThemeStyle.BODY_LARGE, color="grey")
        
        self.card_last_product = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.Icons.INFO_OUTLINE_ROUNDED, color=ACCENT),
                    ft.Text("Último Producto", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, weight="bold")
                ]),
                ft.Divider(height=10),
                self.lbl_last_prod_name,
                self.lbl_last_prod_price,
                self.lbl_last_prod_sku,
            ], spacing=5),
            bgcolor="surfacevariant",
            border_radius=CARD_RADIUS,
            padding=20,
        )

        # Panel de Totales
        self.lbl_total = ft.Text("$ 0.00", theme_style=ft.TextThemeStyle.DISPLAY_SMALL, weight="bold", color="white")

        self.btn_confirm = ft.FilledButton(
            "Confirmar",
            icon=ft.icons.Icons.CHECK_CIRCLE_ROUNDED,
            on_click=self._open_confirm_modal,
            style=ft.ButtonStyle(
                bgcolor="white",
                color=SUCCESS,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding(left=25, top=16, right=25, bottom=16),
            ),
            height=55,
        )

        panel_totales = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("TOTAL A PAGAR", theme_style=ft.TextThemeStyle.BODY_LARGE, color="white70"),
                        self.lbl_total,
                    ], spacing=0),
                    self.btn_confirm
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ]),
            bgcolor=SUCCESS,
            border_radius=CARD_RADIUS,
            padding=ft.Padding(left=20, top=20, right=20, bottom=20),
        )

        right_column = ft.Column([
            self.card_last_product,
            ft.Container(expand=True), # Spacer
            panel_totales
        ], expand=3, spacing=15)

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.icons.Icons.LOCAL_SHIPPING_ROUNDED, size=28, color=ACCENT),
                        ft.Text("Registro de Compras", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold"),
                    ],
                    spacing=10,
                ),
                ft.Row([left_column, right_column], expand=True, spacing=15, vertical_alignment=ft.CrossAxisAlignment.STRETCH)
            ],
            expand=True,
        )

        # Modal Supplier
        sup_options = [ft.dropdown.Option(str(c.id), c.name) for c in self.suppliers]
        self.dd_supplier = ft.Dropdown(
            label="Buscar Proveedor",
            options=sup_options,
            value=str(self.suppliers[0].id) if self.suppliers else None,
            width=300,
        )
        if self.suppliers:
            self._selected_supplier_id = str(self.suppliers[0].id)

    def handle_search(self, e):
        query = self.txt_search.value.lower()
        if len(query) == 0:
            self.search_results_container.visible = False
            self.search_results.controls.clear()
            self.search_results_container.update()
            return
            
        results = []
        for p in self.products:
            searchable_text = f"{p.name} {p.barcode or ''} {p.sku or ''}".lower()
            if query in searchable_text:
                results.append(
                    ft.Container(
                        content=ft.Text(f"{p.name} - Costo Actual: ${p.cost_price or 0:.2f} (Cód: {p.barcode or '-'})", size=14),
                        padding=12,
                        ink=True,
                        border=ft.Border(bottom=ft.BorderSide(1, "black12")),
                        on_click=self.create_select_handler(p.id)
                    )
                )
        self.search_results.controls = results[:30]
        self.search_results_container.visible = len(results) > 0
        self.search_results_container.update()

    def create_select_handler(self, prod_id):
        return lambda e: self._select_product(prod_id)

    def _select_product(self, prod_id):
        self.search_results_container.visible = False
        self.search_results.controls.clear()
        self.txt_search.value = ""
        self.txt_search.update()
        self.search_results_container.update()

        prod = next((p for p in self.products if str(p.id) == str(prod_id)), None)
        if not prod:
            return

        self.last_product = prod
        self.lbl_last_prod_name.value = prod.name
        self.lbl_last_prod_price.value = f"$ {prod.cost_price:,.2f}"
        self.lbl_last_prod_sku.value = f"SKU: {prod.sku or '-'}"

        existing = next((i for i in self.cart_items if i["product_id"] == prod.id), None)
        if existing:
            existing["qty"] += 1
        else:
            self.cart_items.append({
                "product_id": prod.id,
                "name": prod.name,
                "qty": 1,
                "cost": float(prod.cost_price),
            })

        self._update_cart_ui()

    def update_quantity(self, prod_id, delta):
        for item in self.cart_items:
            if item["product_id"] == prod_id:
                item["qty"] += delta
                if item["qty"] <= 0:
                    self.cart_items.remove(item)
                break
        self._update_cart_ui()
        
    def update_cost(self, prod_id, new_val):
        try:
            new_cost = float(new_val)
        except ValueError:
            return
        for item in self.cart_items:
            if item["product_id"] == prod_id:
                item["cost"] = new_cost
                break
        self._update_cart_ui()

    def remove_from_cart(self, prod_id):
        self.cart_items = [i for i in self.cart_items if i["product_id"] != prod_id]
        self._update_cart_ui()

    def clear_cart(self, e=None):
        self.cart_items = []
        if self.suppliers:
            self._selected_supplier_id = str(self.suppliers[0].id)
            self.dd_supplier.value = str(self.suppliers[0].id)
        
        self.last_product = None
        self.lbl_last_prod_name.value = "Ningún producto"
        self.lbl_last_prod_price.value = "$ 0.00"
        self.lbl_last_prod_sku.value = "SKU: -"
        
        self._update_cart_ui()

    def _update_cart_ui(self):
        rows = []
        total = 0.0

        for item in self.cart_items:
            sub = item["qty"] * item["cost"]
            total += sub
            
            txt_cost_input = ft.TextField(
                value=f"{item['cost']:.2f}", 
                width=80, 
                height=35,
                content_padding=5,
                text_align=ft.TextAlign.RIGHT,
                on_change=lambda e, pid=item["product_id"]: self.update_cost(pid, e.control.value)
            )
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["name"])),
                        ft.DataCell(ft.Text(str(int(item["qty"])), weight="bold")),
                        ft.DataCell(ft.Row([ft.Text("$"), txt_cost_input], spacing=2)),
                        ft.DataCell(ft.Text(f"${sub:,.2f}", weight="bold")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.icons.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, icon_color="green", icon_size=18, on_click=lambda e, pid=item["product_id"]: self.update_quantity(pid, 1)),
                                ft.IconButton(ft.icons.Icons.REMOVE_CIRCLE_OUTLINE_ROUNDED, icon_color="orange", icon_size=18, on_click=lambda e, pid=item["product_id"]: self.update_quantity(pid, -1)),
                                ft.IconButton(ft.icons.Icons.DELETE_ROUNDED, icon_color="red", icon_size=18, on_click=lambda e, pid=item["product_id"]: self.remove_from_cart(pid)),
                            ], spacing=0)
                        ),
                    ]
                )
            )

        self.cart_table.rows = rows

        if rows:
            self.cart_content.controls = [self.cart_table]
        else:
            self.cart_content.controls = [self.lbl_empty_cart]

        self.lbl_total.value = f"${total:,.2f}"
        self.update()

    def _get_cart_total(self):
        return sum(i["qty"] * i["cost"] for i in self.cart_items)

    def _open_confirm_modal(self, e):
        if not self.cart_items:
            self.show_snack("El carrito de compras está vacío.")
            return

        total = self._get_cart_total()

        detail_rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["name"])),
                ft.DataCell(ft.Text(str(int(item["qty"])), text_align=ft.TextAlign.RIGHT)),
                ft.DataCell(ft.Text(f"${item['cost']:,.2f}", text_align=ft.TextAlign.RIGHT)),
                ft.DataCell(ft.Text(f"${item['qty'] * item['cost']:,.2f}", weight="bold", text_align=ft.TextAlign.RIGHT)),
            ])
            for item in self.cart_items
        ]

        detail_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Cant."), numeric=True),
                ft.DataColumn(ft.Text("Costo Unit."), numeric=True),
                ft.DataColumn(ft.Text("Subtotal"), numeric=True),
            ],
            rows=detail_rows,
            heading_row_color="surfacevariant",
        )

        dlg = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.icons.Icons.INVENTORY_2_ROUNDED, color=PRIMARY, size=28),
                    ft.Text("Confirmar Ingreso de Mercadería", weight="bold"),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text("Detalle del ingreso:", weight="bold"),
                    ft.Container(
                        content=ft.Column([detail_table], scroll=ft.ScrollMode.AUTO),
                        height=150,
                        border_radius=CARD_RADIUS,
                    ),
                    ft.Divider(),
                    ft.Row([
                        ft.Column([
                            ft.Text("Seleccione Proveedor:", size=12, color="grey"),
                            self.dd_supplier
                        ], spacing=5)
                    ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.START),
                    ft.Divider(),
                    ft.Row([
                        ft.Text("TOTAL DE LA COMPRA:", theme_style=ft.TextThemeStyle.TITLE_LARGE, weight="bold"),
                        ft.Text(f"${total:,.2f}", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold", color=PRIMARY)
                    ], alignment=ft.MainAxisAlignment.END, spacing=10)
                ],
                tight=True,
                spacing=10,
                width=750,
            ),
            actions=[
                ft.FilledButton(
                    "Cancelar",
                    icon=ft.icons.Icons.CANCEL_ROUNDED,
                    on_click=lambda _: self.page.pop_dialog(),
                    style=ft.ButtonStyle(
                        bgcolor=DANGER,
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=5),
                    ),
                ),
                ft.FilledButton(
                    "Registrar",
                    icon=ft.icons.Icons.CHECK_CIRCLE_ROUNDED,
                    on_click=lambda e: self.process_purchase(),
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY,
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=5),
                        padding=ft.Padding(left=30, top=12, right=30, bottom=12),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def process_purchase(self):
        supplier_id = self.dd_supplier.value
        if not supplier_id:
            self.show_snack("Es necesario seleccionar un proveedor en el modal.")
            return
            
        total = self._get_cart_total()

        from database.models.Branch import Branch
        from database.models.User import User
        with get_db() as db:
            branch = db.query(Branch).first()
            if not branch:
                self.page.pop_dialog()
                self.show_snack("Error: No hay sucursales en la base de datos.")
                return
            
            user = db.query(User).first()
            user_id = str(user.id) if user else None

        purchase_data = {
            "branch_id": str(branch.id),
            "user_id": user_id,
            "supplier_id": supplier_id,
            "total_amount": total,
        }

        details_data = [
            {
                "product_id": str(item["product_id"]),
                "quantity": item["qty"],
                "unit_cost": item["cost"],
            }
            for item in self.cart_items
        ]

        try:
            process_purchase_transaction(purchase_data, details_data)
            self.page.pop_dialog()
            
            def on_success_close(e):
                self.page.pop_dialog()
                self.clear_cart()
                
            success_dlg = ft.AlertDialog(
                title=ft.Row([ft.Icon(ft.icons.Icons.CHECK_CIRCLE_ROUNDED, color="green", size=40), ft.Text("¡Ingreso Exitoso!", size=24, weight="bold")]),
                content=ft.Text("La mercadería ha ingresado y el stock se actualizó correctamente.", size=16),
                actions=[
                    ft.FilledButton("Aceptar", on_click=on_success_close, style=ft.ButtonStyle(bgcolor=PRIMARY, color="white"))
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.show_dialog(success_dlg)
            
        except Exception as ex:
            self.page.pop_dialog()
            self.show_snack(f"Error al registrar ingreso: {ex}")

    def show_snack(self, message):
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()
