import flet as ft
from services.product_service import product_service
from services.tax_service import tax_service
from database.db import get_db
from flet_ui.components.paginated_table import PaginatedTable

class ProductsView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        
        self.primary_color = "#6200ee"
        
        self.table = PaginatedTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("SKU")),
                ft.DataColumn(ft.Text("Cód. Barra")),
                ft.DataColumn(ft.Text("Precio Venta")),
                ft.DataColumn(ft.Text("Costo")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            fetch_data_callback=self._fetch_products,
            build_row_callback=self._build_product_row,
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
                ft.Text("📦 Administración de Productos", size=28, weight="bold"),
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
                self.table,
            ],
            expand=True
        )

    def _fetch_products(self, skip, limit):
        with get_db() as db:
            return product_service.get_all(db, skip=skip, limit=limit)

    def handle_row_select(self, e, product_id):
        if e.control.selected:
            self.selected_item_id = product_id
            for row in self.table.table.rows:
                if row.data != product_id:
                    row.selected = False
            self.btn_view.disabled = False
            self.btn_delete.disabled = False
        else:
            self.selected_item_id = None
            self.btn_view.disabled = True
            self.btn_delete.disabled = True
        self.update()

    def handle_double_tap(self, e, product_id):
        self.selected_item_id = product_id
        for row in self.table.table.rows:
            row.selected = (row.data == product_id)
        self.btn_view.disabled = False
        self.btn_delete.disabled = False
        self.update()
        self.view_selected(e)

    def _build_product_row(self, product):
        def on_dbl_click(e):
            self.handle_double_tap(e, product.id)
            
        return ft.DataRow(
            data=product.id,
            on_select_change=lambda e: self.handle_row_select(e, product.id),
            selected=(self.selected_item_id == product.id),
            cells=[
                ft.DataCell(ft.Text(product.name), on_double_tap=on_dbl_click),
                ft.DataCell(ft.Text(product.sku or "-"), on_double_tap=on_dbl_click),
                ft.DataCell(ft.Text(product.barcode or "-"), on_double_tap=on_dbl_click),
                ft.DataCell(ft.Text(f"${product.sale_price:.2f}"), on_double_tap=on_dbl_click),
                ft.DataCell(ft.Text(f"${product.cost_price:.2f}"), on_double_tap=on_dbl_click),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(icon=ft.icons.Icons.EDIT, icon_color="blue", tooltip="Editar", on_click=lambda e: self.open_form_modal(e, product.id)),
                        ft.IconButton(icon=ft.icons.Icons.DELETE, icon_color="red", tooltip="Eliminar", on_click=lambda e: self.confirm_delete(product.id))
                    ])
                ),
            ]
        )

    def open_add_modal(self, e):
        txt_name = ft.TextField(label="Nombre del Producto (*)", width=300, autofocus=True)
        txt_sku = ft.TextField(label="SKU (*)", width=150)
        txt_barcode = ft.TextField(label="Cód. Barras", width=150)
        txt_sale = ft.TextField(label="Precio Venta", width=150, value="0.00")
        txt_cost = ft.TextField(label="Costo", width=150, value="0.00")
        
        # Obtenemos impuestos de forma síncrona simple para el ejemplo
        with get_db() as db:
            taxes = tax_service.get_all(db)
            
    def open_form_modal(self, e, product_id=None):
        product = None
        if product_id:
            with get_db() as db:
                product = product_service.get(db, product_id)

        with get_db() as db:
            taxes = tax_service.get_all(db)
            
        # Campos del formulario
        txt_name = ft.TextField(label="Nombre del Producto (*)", width=300, autofocus=True, value=product.name if product else "")
        txt_sku = ft.TextField(label="SKU", width=150, value=product.sku if product else "")
        txt_barcode = ft.TextField(label="Cód. de Barras", width=150, value=product.barcode if product else "")
        txt_sale_price = ft.TextField(label="Precio Venta (*)", width=150, prefix_text="$", value=str(product.sale_price) if product else "")
        txt_cost_price = ft.TextField(label="Costo (*)", width=150, prefix_text="$", value=str(product.cost_price) if product else "")
        
        dd_tax = ft.Dropdown(
            label="Impuesto",
            width=300,
            options=[ft.dropdown.Option(str(t.id), text=f"{t.name} ({t.rate}%)") for t in taxes] if taxes else []
        )
        if product and product.tax_id:
            dd_tax.value = str(product.tax_id)
        elif taxes:
            dd_tax.value = str(taxes[0].id)
            
        # Validar y guardar
        def save_product(e2):
            val_name = (txt_name.value or "").strip()
            val_sale = (txt_sale_price.value or "").strip()
            val_cost = (txt_cost_price.value or "").strip()
            val_sku = (txt_sku.value or "").strip()
            val_barcode = (txt_barcode.value or "").strip()
            
            if not val_name or not val_sale or not val_cost or not dd_tax.value:
                self.page.snack_bar = ft.SnackBar(ft.Text("Complete los campos obligatorios (Nombre, Precios, Impuesto)"))
                self.page.snack_bar.open = True
                self.page.update()
                return
                
            try:
                sale = float(val_sale)
                cost = float(val_cost)
            except ValueError:
                self.page.snack_bar = ft.SnackBar(ft.Text("Precios inválidos"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            product_data = {
                "name": val_name,
                "sku": val_sku or None,
                "barcode": val_barcode or None,
                "sale_price": sale,
                "cost_price": cost,
                "tax_id": dd_tax.value
            }
            
            with get_db() as db:
                if product_id:
                    db_product = product_service.get(db, product_id)
                    product_service.update(db, db_product, product_data)
                else:
                    product_service.create(db, product_data)
            
            self.page.pop_dialog()
            self.table.refresh()
            
        def close_dlg(d):
            self.page.pop_dialog()

        dlg = ft.AlertDialog(
            title=ft.Text("Editar Producto" if product_id else "Nuevo Producto"),
            content=ft.Column(
                [
                    txt_name,
                    ft.Row([txt_sku, txt_barcode]),
                    ft.Row([txt_cost_price, txt_sale_price]),
                    dd_tax,
                ],
                tight=True,
                spacing=15
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dlg(dlg), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))),
                ft.FilledButton("Guardar", on_click=save_product, style=ft.ButtonStyle(bgcolor=self.primary_color, color="white", shape=ft.RoundedRectangleBorder(radius=5))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.show_dialog(dlg)

    def view_selected(self, e):
        if not self.selected_item_id:
            return
            
        with get_db() as db:
            product = product_service.get(db, self.selected_item_id)
            if not product:
                return

        def close_dlg(page, dialog):
            dialog.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalles del Producto: {product.name}"),
            content=ft.Column([
                ft.Text(f"ID: {product.id}", weight="bold"),
                ft.Text(f"Nombre: {product.name}"),
                ft.Text(f"SKU: {product.sku or 'N/A'}"),
                ft.Text(f"Código de Barras: {product.barcode or 'N/A'}"),
                ft.Text(f"Precio Venta: ${product.sale_price:.2f}"),
                ft.Text(f"Costo: ${product.cost_price:.2f}"),
                ft.Text(f"Stock Mín/Máx: {product.min_stock} / {product.max_stock}"),
                ft.Text(f"Descripción: {product.description or 'N/A'}"),
                ft.Text(f"Activo: {'Sí' if product.is_active else 'No'}"),
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

    def confirm_delete(self, product_id):
        def on_yes(e2):
            with get_db() as db:
                product_service.soft_delete(db, product_id)
            self.page.pop_dialog()
            self.table.refresh()
            
        dlg = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Estás seguro que deseas eliminar este producto?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dlg(dlg), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))),
                ft.TextButton("Eliminar", on_click=on_yes, style=ft.ButtonStyle(color="red", shape=ft.RoundedRectangleBorder(radius=5))),
            ]
        )
        
        def close_dlg(d):
            self.page.pop_dialog()

        self.page.show_dialog(dlg)
