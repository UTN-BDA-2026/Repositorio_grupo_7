import flet as ft
import subprocess
import os
import tempfile
from datetime import datetime
from nosql.events import log_event

ACCENT = "#3498db"
SUCCESS = "#27ae60"
PRIMARY = "#007bff"

class BackupView(ft.Container):
    def __init__(self, current_user):
        super().__init__()
        self.expand = True
        self.padding = 30
        self.current_user = current_user
        
        self.script_path = os.path.abspath(os.path.join(os.getcwd(), "scripts", "backup.sh"))
        
        self.status_text = ft.Text("", color=SUCCESS, weight="bold")
        
        # Immediate Backup
        self.btn_immediate = ft.FilledButton(
            "Hacer Respaldo Inmediato",
            icon=ft.icons.Icons.CLOUD_DOWNLOAD_ROUNDED,
            on_click=self.trigger_immediate,
            style=ft.ButtonStyle(bgcolor=PRIMARY, color="white", padding=20)
        )
        
        # Schedule Backup
        self.dd_freq = ft.Dropdown(
            label="Frecuencia",
            width=300,
            options=[
                ft.dropdown.Option("nunca", "Desactivado"),
                ft.dropdown.Option("0 0 * * *", "Diario (a la medianoche)"),
                ft.dropdown.Option("0 0 * * 0", "Semanal (Domingo a la medianoche)"),
                ft.dropdown.Option("0 * * * *", "Cada hora"),
            ],
            value="nunca"
        )
        
        self.btn_schedule = ft.FilledButton(
            "Guardar Programación",
            icon=ft.icons.Icons.SCHEDULE_ROUNDED,
            on_click=self.save_schedule,
            style=ft.ButtonStyle(bgcolor=ACCENT, color="white", padding=20)
        )

        self.list_backups = ft.ListView(expand=True, spacing=10)
        
        self.content = ft.Column(
            [
                ft.Text("Respaldos de Base de Datos", size=28, weight="bold"),
                ft.Divider(height=20, color="transparent"),
                
                ft.Row([self.btn_immediate], alignment=ft.MainAxisAlignment.START),
                
                ft.Divider(height=30, color="grey30"),
                
                ft.Text("Programar Respaldos Automáticos", size=20, weight="bold"),
                ft.Text("Los respaldos automáticos se ejecutarán en el servidor mediante Cron.", color="grey50"),
                ft.Row([self.dd_freq, self.btn_schedule]),
                
                self.status_text,
                
                ft.Divider(height=30, color="grey30"),
                ft.Text("Respaldos Existentes", size=20, weight="bold"),
                ft.Container(
                    content=self.list_backups,
                    expand=True,
                    border=ft.Border(
                        top=ft.BorderSide(1, "grey30"),
                        right=ft.BorderSide(1, "grey30"),
                        bottom=ft.BorderSide(1, "grey30"),
                        left=ft.BorderSide(1, "grey30")
                    ),
                    border_radius=8,
                    padding=10
                )
            ],
            expand=True
        )
        
        self.load_backups()
        self.load_current_cron()

    def load_backups(self):
        self.list_backups.controls.clear()
        backups_dir = os.path.join(os.getcwd(), "backups")
        if os.path.exists(backups_dir):
            files = sorted(os.listdir(backups_dir), reverse=True)
            for f in files:
                if f.endswith(".dump"):
                    self.list_backups.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.Icons.STORAGE_ROUNDED, color=PRIMARY),
                            title=ft.Text(f),
                            subtitle=ft.Text(f"Tamaño: {os.path.getsize(os.path.join(backups_dir, f)) / 1024:.2f} KB")
                        )
                    )
        if not self.list_backups.controls:
            self.list_backups.controls.append(ft.Text("No hay respaldos creados.", color="grey50"))

    def load_current_cron(self):
        try:
            current_cron = subprocess.check_output(["crontab", "-l"]).decode('utf-8')
            for line in current_cron.splitlines():
                if "backup.sh" in line:
                    parts = line.split(" /bin/bash")[0]
                    # Attempt to match the cron expression with our dropdown options
                    for opt in self.dd_freq.options:
                        if opt.key == parts:
                            self.dd_freq.value = parts
                            return
            self.dd_freq.value = "nunca"
        except subprocess.CalledProcessError:
            self.dd_freq.value = "nunca"

    def trigger_immediate(self, e):
        def close_dlg(ev):
            if hasattr(self.page, "pop_dialog"):
                self.page.pop_dialog()
            else:
                self.page.close_dialog()

        try:
            subprocess.run(["bash", self.script_path], capture_output=True, text=True, check=True)
            log_event("backup_created", {
                "type": "manual",
                "user_id": str(self.current_user.id) if self.current_user else "admin"
            })
            
            dlg = ft.AlertDialog(
                title=ft.Text("Respaldo Exitoso", color=SUCCESS),
                content=ft.Text("El respaldo se ha creado correctamente en la carpeta backups/."),
                actions=[ft.TextButton("Entendido", on_click=close_dlg)]
            )
            self.load_backups()
            self.update()
        except subprocess.CalledProcessError as err:
            dlg = ft.AlertDialog(
                title=ft.Text("Error en Respaldo", color=DANGER),
                content=ft.Text(f"Falló la ejecución:\n{err.stderr}"),
                actions=[ft.TextButton("Cerrar", on_click=close_dlg)]
            )
            
        if hasattr(self.page, "show_dialog"):
            self.page.show_dialog(dlg)
        else:
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

    def save_schedule(self, e):
        freq = self.dd_freq.value
        try:
            try:
                current_cron = subprocess.check_output(["crontab", "-l"]).decode('utf-8')
            except subprocess.CalledProcessError:
                current_cron = ""
                
            lines = [line for line in current_cron.splitlines() if "backup.sh" not in line]
            
            if freq != "nunca":
                lines.append(f"{freq} /bin/bash {self.script_path}")
                
            new_cron = "\n".join(lines) + "\n"
            
            with tempfile.NamedTemporaryFile('w', delete=False) as f:
                f.write(new_cron)
                tmp_name = f.name
                
            subprocess.run(["crontab", tmp_name])
            os.remove(tmp_name)
            
            log_event("backup_schedule_updated", {
                "cron": freq,
                "user_id": str(self.current_user.id) if self.current_user else "admin"
            })
            
            self.status_text.value = "Programación guardada exitosamente."
            self.update()
            
        except Exception as ex:
            self.status_text.value = f"Error al guardar programación: {ex}"
            self.status_text.color = DANGER
            self.update()

