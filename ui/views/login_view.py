import flet as ft
from database.db import get_db
from database.models.User import User

class LoginView(ft.Container):
    def __init__(self, on_login_success):
        super().__init__()
        self.expand = True
        self.on_login_success = on_login_success
        self.alignment = ft.Alignment(0, 0)
        self.bgcolor = "#ecf0f1"
        
        self.txt_email = ft.TextField(
            label="Email / PIN Caja",
            prefix_icon=ft.icons.Icons.PERSON_ROUNDED,
            width=300,
            autofocus=True
        )
        self.txt_password = ft.TextField(
            label="Contraseña",
            prefix_icon=ft.icons.Icons.LOCK_ROUNDED,
            password=True,
            can_reveal_password=True,
            width=300,
            on_submit=self.do_login
        )
        self.btn_login = ft.FilledButton(
            "Ingresar",
            width=300,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor="#e74c3c",
                color="white"
            ),
            on_click=self.do_login
        )
        
        self.lbl_error = ft.Text(color="red", visible=False)

        card = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.icons.Icons.STORE_ROUNDED, size=64, color="#e74c3c"),
                    ft.Text("Bienvenido al POS", size=24, weight="bold"),
                    ft.Text("Ingresá tus credenciales para continuar", color="grey", size=14),
                    ft.Container(height=20),
                    self.txt_email,
                    self.txt_password,
                    self.lbl_error,
                    ft.Container(height=10),
                    self.btn_login
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="white",
            padding=40,
            border_radius=10,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color="black12"),
        )
        
        self.content = card

    def do_login(self, e):
        email_or_pin = self.txt_email.value.strip()
        password = self.txt_password.value.strip()
        
        if not email_or_pin or not password:
            self.show_error("Completá ambos campos.")
            return
            
        with get_db() as db:
            # Intentar primero por email, luego por PIN (útil para cajeros rápidos)
            user = db.query(User).filter(
                (User.email == email_or_pin) | (User.pos_pin == email_or_pin)
            ).first()
            
            if user and user.password == password:
                if getattr(user, 'is_active', True) is False:
                    self.show_error("Usuario inactivo.")
                else:
                    self.on_login_success(user)
            else:
                self.show_error("Credenciales incorrectas.")

    def show_error(self, msg):
        self.lbl_error.value = msg
        self.lbl_error.visible = True
        self.update()
