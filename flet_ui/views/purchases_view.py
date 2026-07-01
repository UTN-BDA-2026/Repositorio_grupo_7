import flet as ft
from database.db import get_db
from database.transactions import process_purchase_transaction
from services.supplier_service import supplier_service
from services.product_service import product_service


ACCENT = "#3498db"
SUCCESS = "#27ae60"
CARD_RADIUS = 10
SECTION_HEIGHT = 120


class PurchasesView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30

        self.suppliers = []
        self.products = []
        self.cart_items = []
        self._selected_supplier_id = None
        self._selected_supplier_name = "Seleccione un Proveedor"
        self._selected_product_id = None

        with get_db() as db:
            self.suppliers = supplier_service.get_all(db, limit=1000)
            self.products = product_service.get_all(db, limit=1000)

        # Buscador de Proveedores (Nativo para soportar overlay responsive)
        ac_supplier_suggestions = [
            ft.AutoCompleteSuggestion(key=str(s.id), value=s.name)
            for s in self.suppliers
        ]
        self.ac_supplier = ft.AutoComplete(
            suggestions=ac_supplier_suggestions,
            on_select=self._on_supplier_selected,
        )

        # Buscador de Productos (Múltiples alias para mejorar coincidencias)
        ac_product_suggestions = []
        for p in self.products:
            # Por nombre
            ac_product_suggestions.append(ft.AutoCompleteSuggestion(
                key=str(p.id),
                value=f"{p.name} - Costo: ${p.cost_price or 0:.2f}"
            ))
            # Por código de barras
            if p.barcode:
                ac_product_suggestions.append(ft.AutoCompleteSuggestion(
                    key=str(p.id),
                    value=f"{p.barcode} - {p.name} - Costo: ${p.cost_price or 0:.2f}"
                ))
            # Por SKU
            if p.sku and p.sku != p.barcode:
                ac_product_suggestions.append(ft.AutoCompleteSuggestion(
                    key=str(p.id),
                    value=f"{p.sku} - {p.name} - Costo: ${p.cost_price or 0:.2f}"
                ))

        self.ac_product = ft.AutoComplete(
            suggestions=ac_product_suggestions,
            on_select=self._on_product_selected,
        )

        self.txt_qty = ft.TextField(
            label="Cant.",
            value="1",
            width=80,
            text_align=ft.TextAlign.CENTER,
            border_radius=8,
        )
        
        self.txt_cost = ft.TextField(
            label="Costo Unit.",
            value="0.00",
            width=120,
            text_align=ft.TextAlign.RIGHT,
            border_radius=8,
            prefix=ft.Text("$")
        )

        self.btn_add = ft.FilledButton(
            "Agregar",
            icon=ft.icons.Icons.ADD_SHOPPING_CART_ROUNDED,
            on_click=self.add_to_cart,
            style=ft.ButtonStyle(
                bgcolor=ACCENT,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding(left=20, top=14, right=20, bottom=14),
            ),
        )

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
        )

        self.lbl_total = ft.Text(
            "$0.00", size=32, weight="bold", color="white"
        )

        self.btn_confirm = ft.FilledButton(
            "Confirmar Ingreso",
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

        self.lbl_empty_cart = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.icons.Icons.INVENTORY_2_OUTLINED,
                        size=48,
                        color="grey",
                    ),
                    ft.Text(
                        "No hay productos en esta compra",
                        size=16,
                        color="grey",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Buscá y agregá mercadería para ingresar",
                        size=12,
                        color="grey",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

        self.cart_content = ft.Column(
            [self.lbl_empty_cart],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        section_supplier = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.Icons.LOCAL_SHIPPING_ROUNDED, size=20, color=ACCENT),
                            ft.Text("Proveedor", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, weight="bold"),
                        ],
                        spacing=8,
                    ),
                    ft.Text("Buscá y seleccioná un proveedor", size=12, color="grey"),
                    self.ac_supplier,
                ],
                spacing=5,
            ),
            bgcolor="surfacevariant",
            border_radius=CARD_RADIUS,
            padding=20,
            height=SECTION_HEIGHT,
            col={"xs": 12, "md": 4},
        )

        section_product = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.Icons.SEARCH_ROUNDED, size=20, color=ACCENT),
                            ft.Text("Agregar Producto Ingresante", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, weight="bold"),
                        ],
                        spacing=8,
                    ),
                    ft.Row(
                        [
                            ft.Container(self.ac_product, expand=True),
                            self.txt_qty,
                            self.txt_cost,
                            self.btn_add,
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor="surfacevariant",
            border_radius=CARD_RADIUS,
            padding=20,
            height=SECTION_HEIGHT,
            col={"xs": 12, "md": 8},
        )

        section_cart = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.icons.Icons.FORMAT_LIST_BULLETED_ROUNDED,
                                size=20,
                                color=ACCENT,
                            ),
                            ft.Text("Detalle de la Compra", size=16, weight="bold"),
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
            expand=True,
        )

        total_bar = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("TOTAL A PAGAR", size=12, color="white70"),
                            self.lbl_total,
                        ],
                        spacing=0,
                    ),
                    self.btn_confirm,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=SUCCESS,
            border_radius=CARD_RADIUS,
            padding=ft.Padding(left=25, top=15, right=25, bottom=15),
        )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(
                            ft.icons.Icons.SHOPPING_BAG_ROUNDED,
                            size=28,
                            color=ACCENT,
                        ),
                        ft.Text("Registro de Compras", size=26, weight="bold"),
                    ],
                    spacing=10,
                ),
                ft.Container(height=10),
                ft.ResponsiveRow(
                    [section_supplier, section_product],
                    spacing=15,
                    run_spacing=15,
                ),
                ft.Container(height=10),
                section_cart,
                ft.Container(height=10),
                total_bar,
            ],
            expand=True,
        )

    def _on_supplier_selected(self, e):
        self._selected_supplier_id = e.selection.key
        self._selected_supplier_name = e.selection.value
        self.show_snack(f"Proveedor seleccionado: {e.selection.value}")

    def _on_product_selected(self, e):
        self._selected_product_id = e.selection.key
        prod = next((p for p in self.products if str(p.id) == self._selected_product_id), None)
        if prod:
            self.txt_cost.value = f"{prod.cost_price:.2f}" if prod.cost_price else "0.00"
        self.update()

    def add_to_cart(self, e):
        if not self._selected_product_id:
            self.show_snack("Seleccioná un producto del buscador.")
            return

        try:
            qty = float(self.txt_qty.value)
            if qty <= 0:
                raise ValueError
            
            cost = float(self.txt_cost.value)
            if cost < 0:
                raise ValueError
        except ValueError:
            self.show_snack("Cantidad o costo inválido.")
            return

        prod = next(
            (p for p in self.products if str(p.id) == self._selected_product_id),
            None,
        )
        if not prod:
            return

        existing = next(
            (i for i in self.cart_items if i["product_id"] == prod.id and i["cost"] == cost), None
        )
        if existing:
            existing["qty"] += qty
        else:
            self.cart_items.append({
                "product_id": prod.id,
                "name": prod.name,
                "qty": qty,
                "cost": cost,
            })

        self._selected_product_id = None
        self.ac_product.value = ""
        self.txt_qty.value = "1"
        self.txt_cost.value = "0.00"
        self._update_cart_ui()

    def remove_from_cart(self, prod_id, cost):
        self.cart_items = [i for i in self.cart_items if not (i["product_id"] == prod_id and i["cost"] == cost)]
        self._update_cart_ui()

    def _update_cart_ui(self):
        rows = []
        total = 0.0

        for item in self.cart_items:
            sub = item["qty"] * item["cost"]
            total += sub
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["name"])),
                        ft.DataCell(ft.Text(str(int(item["qty"])))),
                        ft.DataCell(ft.Text(f"${item['cost']:,.2f}")),
                        ft.DataCell(
                            ft.Text(f"${sub:,.2f}", weight="bold")
                        ),
                        ft.DataCell(
                            ft.IconButton(
                                ft.icons.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color="red",
                                tooltip="Quitar",
                                on_click=lambda e, pid=item["product_id"], c=item["cost"]: self.remove_from_cart(pid, c),
                            )
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
            self.show_snack("No hay productos para ingresar.")
            return
            
        if not self._selected_supplier_id:
            self.show_snack("Es necesario seleccionar un proveedor.")
            return

        total = self._get_cart_total()

        detail_rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["name"])),
                ft.DataCell(ft.Text(str(int(item["qty"])))),
                ft.DataCell(ft.Text(f"${item['cost']:,.2f}")),
                ft.DataCell(ft.Text(f"${item['qty'] * item['cost']:,.2f}", weight="bold")),
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
                    ft.Icon(ft.icons.Icons.CHECK_CIRCLE_ROUNDED, color=SUCCESS, size=28),
                    ft.Text("Confirmar Ingreso de Mercadería", weight="bold"),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Row([
                        ft.Text("Proveedor:", weight="bold"),
                        ft.Text(self._selected_supplier_name),
                    ], spacing=10),
                    ft.Divider(),
                    ft.Text("Detalle del ingreso:", weight="bold"),
                    ft.Column(
                        [detail_table],
                        scroll=ft.ScrollMode.AUTO,
                        height=200,
                    ),
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.Container(expand=True),
                            ft.Column(
                                [
                                    ft.Text("Total de la compra", size=12, color="grey"),
                                    ft.Text(
                                        f"${total:,.2f}",
                                        size=28,
                                        weight="bold",
                                        color=SUCCESS,
                                    ),
                                ],
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                tight=True,
                spacing=10,
                width=600,
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda _: self.page.pop_dialog(),
                    style=ft.ButtonStyle(
                        color="grey",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
                ft.FilledButton(
                    "Confirmar",
                    icon=ft.icons.Icons.SAVE_ROUNDED,
                    on_click=lambda e: self._process_purchase(),
                    style=ft.ButtonStyle(
                        bgcolor=SUCCESS,
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding(left=30, top=12, right=30, bottom=12),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def _process_purchase(self):
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
            "supplier_id": self._selected_supplier_id,
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
                self.cart_items = []
                self._selected_supplier_id = None
                self._selected_supplier_name = "Seleccione un Proveedor"
                self.ac_supplier.value = ""
                self.ac_supplier.update()
                self._update_cart_ui()
                
            success_dlg = ft.AlertDialog(
                title=ft.Row([ft.Icon(ft.icons.Icons.CHECK_CIRCLE_ROUNDED, color="green", size=40), ft.Text("¡Ingreso Exitoso!", size=24, weight="bold")]),
                content=ft.Text("La mercadería ha ingresado y el stock se actualizó correctamente.", size=16),
                actions=[
                    ft.FilledButton("Aceptar", on_click=on_success_close, style=ft.ButtonStyle(bgcolor=SUCCESS, color="white"))
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
