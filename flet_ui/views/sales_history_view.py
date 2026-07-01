import flet as ft
from database.db import get_db
from services.sale_service import sale_service
from flet_ui.components.paginated_table import PaginatedTable


class SalesHistoryView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        self.selected_sale = None

        btn_shape = ft.RoundedRectangleBorder(radius=5)

        self.table = PaginatedTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha y Hora")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Método de Pago")),
                ft.DataColumn(ft.Text("Total"), numeric=True),
            ],
            fetch_data_callback=self._fetch_sales,
            build_cells_callback=self._build_sale_cells,
            on_row_click=self._on_row_selected,
            on_row_double_click=self.view_selected,
            page_size=15
        )

        self.content = ft.Column(
            [
                ft.Text("🧾 Historial de Ventas", size=28, weight="bold"),
                ft.Row(
                    [],
                    alignment=ft.MainAxisAlignment.END
                ),
                ft.Divider(height=5, color="transparent"),
                self.table,
            ],
            expand=True
        )

    def _fetch_sales(self, skip, limit):
        with get_db() as db:
            return sale_service.get_paginated(db, skip, limit)

    def _on_row_selected(self, sale):
        self.selected_sale = sale
        self.update()

    def _build_sale_cells(self, sale):
        fecha = sale.created_at.strftime("%d/%m/%Y %H:%M") if sale.created_at else "-"
        cliente = sale.client.name if sale.client else "Sin cliente"
        metodo = sale.payment_method.name if sale.payment_method else "-"
        total = f"${sale.total_amount:,.2f}"

        return [
            ft.DataCell(ft.Text(fecha)),
            ft.DataCell(ft.Text(cliente)),
            ft.DataCell(ft.Text(metodo)),
            ft.DataCell(ft.Text(total)),
        ]

    def view_selected(self, sale):
        if not sale:
            return

        with get_db() as db:
            full_sale, details = sale_service.get_with_details(db, sale.id)
            if not full_sale:
                return

        detail_rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(d.product.name if d.product else str(d.product_id))),
                ft.DataCell(ft.Text(str(int(d.quantity)))),
                ft.DataCell(ft.Text(f"${d.unit_price:,.2f}")),
                ft.DataCell(ft.Text(f"${d.quantity * d.unit_price:,.2f}")),
            ])
            for d in details
        ]

        fecha = full_sale.created_at.strftime("%d/%m/%Y %H:%M") if full_sale.created_at else "-"
        cliente = full_sale.client.name if full_sale.client else "Sin cliente"
        metodo = full_sale.payment_method.name if full_sale.payment_method else "-"

        items_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Cant."), numeric=True),
                ft.DataColumn(ft.Text("Precio unit."), numeric=True),
                ft.DataColumn(ft.Text("Subtotal"), numeric=True),
            ],
            rows=detail_rows,
            border=ft.Border(
                top=ft.BorderSide(1, "#333333"),
                right=ft.BorderSide(1, "#333333"),
                bottom=ft.BorderSide(1, "#333333"),
                left=ft.BorderSide(1, "#333333"),
            ),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, "#222222"),
            heading_row_color="surfacevariant",
        )

        dlg = ft.AlertDialog(
            title=ft.Text(f"Detalle de Venta — {fecha}"),
            content=ft.Column(
                [
                    ft.Row([
                        ft.Text("Cliente:", weight="bold"),
                        ft.Text(cliente),
                        ft.Container(width=20),
                        ft.Text("Método:", weight="bold"),
                        ft.Text(metodo),
                        ft.Container(width=20),
                        ft.Text("Total:", weight="bold"),
                        ft.Text(f"${full_sale.total_amount:,.2f}"),
                    ]),
                    ft.Divider(),
                    ft.Text("Ítems:", weight="bold"),
                    items_table,
                ],
                tight=True,
                spacing=10,
                width=700,
            ),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=lambda _: self.page.pop_dialog(),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                )
            ]
        )
        self.page.show_dialog(dlg)
