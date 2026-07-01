import flet as ft
from nosql.client import db
import json
from datetime import datetime

class AuditView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 30
        
        self.events_list = ft.ListView(expand=True, spacing=15, auto_scroll=False)
        self.btn_refresh = ft.FilledButton(
            "Refrescar", 
            icon=ft.icons.Icons.REFRESH_ROUNDED, 
            on_click=self.load_events,
            style=ft.ButtonStyle(bgcolor="#34495e", color="white")
        )
        self.chk_json_mode = ft.Switch(
            label="Ver JSON Crudo", 
            value=False, 
            on_change=self.load_events
        )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Row([
                            ft.Icon(ft.icons.Icons.HISTORY_ROUNDED, size=28, color="#34495e"),
                            ft.Text("Auditoría del Sistema (NoSQL)", size=28, weight="bold"),
                        ], spacing=10),
                        ft.Row([self.chk_json_mode, self.btn_refresh], spacing=20)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Text("Registro inmutable de eventos guardado en MongoDB.", color="grey"),
                ft.Divider(height=20, color="transparent"),
                self.events_list
            ],
            expand=True
        )

    def did_mount(self):
        self.load_events()

    def load_events(self, e=None):
        self.events_list.controls.clear()
        
        try:
            # Traer los últimos 50 eventos ordenados por fecha descendente
            events = list(db.events.find().sort("created_at", -1).limit(50))
            
            if not events:
                self.events_list.controls.append(ft.Text("No hay eventos registrados aún.", color="grey"))
            else:
                if self.chk_json_mode.value:
                    # MODO JSON (Tarjetas con código puro)
                    for ev in events:
                        self.events_list.controls.append(self._build_json_card(ev))
                else:
                    # MODO TABLA (Tipo historial)
                    self.events_list.controls.append(self._build_main_table(events))
                    
        except Exception as ex:
            self.events_list.controls.append(ft.Text(f"Error al conectar con MongoDB: {ex}", color="red"))
            
        self.update()

    def _build_main_table(self, events):
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Evento")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("ID Referencia")),
                ft.DataColumn(ft.Text("Cajero / Usuario")),
                ft.DataColumn(ft.Text("Artículos", text_align=ft.TextAlign.RIGHT)),
                ft.DataColumn(ft.Text("Monto Total", text_align=ft.TextAlign.RIGHT)),
            ],
            rows=[],
            heading_row_color="surfacevariant",
            border=ft.Border(
                top=ft.BorderSide(1, "#333333"),
                right=ft.BorderSide(1, "#333333"),
                bottom=ft.BorderSide(1, "#333333"),
                left=ft.BorderSide(1, "#333333"),
            ),
            border_radius=10,
            vertical_lines=ft.BorderSide(1, "#222222")
        )

        for event in events:
            ev_type = event.get("type", "unknown")
            created_at = event.get("created_at")
            payload = event.get("payload", {})
            
            if isinstance(created_at, datetime):
                date_str = created_at.strftime("%d/%m/%Y %H:%M:%S")
            else:
                date_str = str(created_at)

            if ev_type == "sale_confirmed":
                ev_type_label = "Venta"
                icon = ft.icons.Icons.RECEIPT_ROUNDED
                color = "#2ecc71"
                ref_id = payload.get("sale_id", "")
            elif ev_type == "purchase_confirmed":
                ev_type_label = "Compra"
                icon = ft.icons.Icons.LOCAL_SHIPPING_ROUNDED
                color = "#f39c12"
                ref_id = payload.get("purchase_id", "")
            else:
                ev_type_label = ev_type.upper()
                icon = ft.icons.Icons.INFO_ROUNDED
                color = "blue"
                ref_id = "-"
                
            user_id = payload.get("user_id", "-")
            items = str(payload.get("items_count", "-"))
            
            total_val = payload.get("total", "-")
            if isinstance(total_val, (int, float)):
                total_str = f"${float(total_val):,.2f}"
            else:
                total_str = str(total_val)

            # Para acortar los UUIDs largos en la tabla
            short_ref = str(ref_id)[:8] + "..." if len(str(ref_id)) > 8 else str(ref_id)
            short_usr = str(user_id)[:8] + "..." if len(str(user_id)) > 8 else str(user_id)

            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row([
                                ft.Icon(icon, color=color, size=16), 
                                ft.Text(ev_type_label, weight="bold", color=color)
                            ], spacing=5)
                        ),
                        ft.DataCell(ft.Text(date_str)),
                        ft.DataCell(ft.Text(short_ref, tooltip=str(ref_id))),
                        ft.DataCell(ft.Text(short_usr, tooltip=str(user_id))),
                        ft.DataCell(ft.Text(items, text_align=ft.TextAlign.RIGHT)),
                        ft.DataCell(ft.Text(total_str, weight="bold", text_align=ft.TextAlign.RIGHT)),
                    ]
                )
            )
            
        return ft.ListView([table], expand=True)

    def _build_json_card(self, event):
        ev_type = event.get("type", "unknown")
        created_at = event.get("created_at")
        payload = event.get("payload", {})
        
        if isinstance(created_at, datetime):
            date_str = created_at.strftime("%d/%m/%Y %H:%M:%S")
        else:
            date_str = str(created_at)

        # Configurar colores e íconos según el tipo de evento
        icon = ft.icons.Icons.INFO_ROUNDED
        color = "blue"
        
        if ev_type == "sale_confirmed":
            icon = ft.icons.Icons.RECEIPT_ROUNDED
            color = "#2ecc71"
            ev_type_label = "Venta Confirmada"
        elif ev_type == "purchase_confirmed":
            icon = ft.icons.Icons.LOCAL_SHIPPING_ROUNDED
            color = "#f39c12"
            ev_type_label = "Ingreso de Mercadería"
        else:
            ev_type_label = ev_type.upper()

        payload_str = json.dumps(payload, indent=2, ensure_ascii=False)
        content_view = ft.Text(payload_str, font_family="monospace", size=12)

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=color),
                        ft.Text(ev_type_label, weight="bold", size=16, color=color),
                        ft.Text(f"— {date_str}", color="grey", size=12)
                    ]),
                    ft.Container(
                        content=content_view,
                        bgcolor="#f1f2f6",
                        padding=15,
                        border_radius=8,
                        width=float("inf")
                    )
                ]),
                padding=15
            ),
            elevation=2
        )
