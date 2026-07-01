import flet as ft


class PaginatedTable(ft.Column):
    def __init__(self, columns, fetch_data_callback, build_cells_callback,
                 on_row_click=None, on_row_double_click=None, page_size=10):
        super().__init__()
        self.expand = True
        self.page_size = page_size
        self.current_page = 0
        self.selected_item = None

        self.fetch_data_callback = fetch_data_callback
        self.build_cells_callback = build_cells_callback
        self.on_row_click = on_row_click
        self.on_row_double_click = on_row_double_click

        btn_shape = ft.RoundedRectangleBorder(radius=5)

        self.table = ft.DataTable(
            columns=columns,
            rows=[],
            border=ft.Border(
                top=ft.BorderSide(1, "#333333"),
                right=ft.BorderSide(1, "#333333"),
                bottom=ft.BorderSide(1, "#333333"),
                left=ft.BorderSide(1, "#333333"),
            ),
            border_radius=10,
            vertical_lines=ft.BorderSide(1, "#222222"),
            heading_row_color="surfacevariant",
        )

        self.btn_prev = ft.FilledButton(
            "Anterior",
            icon=ft.icons.Icons.ARROW_BACK,
            on_click=self.prev_page,
            disabled=True,
            style=ft.ButtonStyle(bgcolor="#444444", color="white", shape=btn_shape)
        )
        self.btn_next = ft.FilledButton(
            "Siguiente",
            icon=ft.icons.Icons.ARROW_FORWARD,
            on_click=self.next_page,
            disabled=True,
            style=ft.ButtonStyle(bgcolor="#444444", color="white", shape=btn_shape)
        )
        self.lbl_page = ft.Text("Página 1", weight="bold", size=16)

        self.pagination_row = ft.Row(
            [self.btn_prev, self.lbl_page, self.btn_next],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.controls = [
            ft.ListView([self.table], expand=True),
            self.pagination_row
        ]

    def did_mount(self):
        self.load_page()

    def _handle_row_click(self, e, item):
        is_same_row = self.selected_item is not None and self.selected_item.id == item.id
        self.selected_item = None if is_same_row else item

        for row in self.table.rows:
            row.selected = (self.selected_item is not None and row.data == self.selected_item.id)

        self.table.update()

        if self.on_row_click:
            self.on_row_click(self.selected_item)

    def _handle_double_click(self, e, item):
        self.selected_item = item

        for row in self.table.rows:
            row.selected = (row.data == item.id)

        self.table.update()

        if self.on_row_double_click:
            self.on_row_double_click(item)

    def load_page(self):
        skip = self.current_page * self.page_size
        data = self.fetch_data_callback(skip, self.page_size + 1)

        has_next = len(data) > self.page_size
        display_data = data[:self.page_size]

        rows = []
        for item in display_data:
            cells = self.build_cells_callback(item)

            if self.on_row_double_click:
                for cell in cells[:-1]:
                    cell.on_double_tap = lambda e, i=item: self._handle_double_click(e, i)

            is_selected = self.selected_item is not None and self.selected_item.id == item.id
            rows.append(ft.DataRow(
                data=item.id,
                cells=cells,
                selected=is_selected,
                on_select_change=lambda e, i=item: self._handle_row_click(e, i),
            ))

        self.table.rows = rows
        self.btn_prev.disabled = (self.current_page == 0)
        self.btn_next.disabled = not has_next
        self.lbl_page.value = f"Página {self.current_page + 1}"
        self.update()

    def next_page(self, e):
        self.current_page += 1
        self.load_page()

    def prev_page(self, e):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page()

    def refresh(self):
        self.current_page = 0
        self.selected_item = None
        self.load_page()
