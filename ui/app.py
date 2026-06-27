import customtkinter as ctk
from ui.views.dashboard_view import DashboardView

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Ventas - Dashboard")
        self.geometry("1100x650")
        
        # Color de fondo de la app: (Color Claro, Color Oscuro)
        self.configure(fg_color=("#f0f2f5", "#0e0f15"))
        
        # Configuración del grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)

        # ==========================================
        # PANEL LATERAL (SIDEBAR)
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="transparent")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # Sección: Menu
        self.lbl_menu = ctk.CTkLabel(self.sidebar_frame, text="Menu", anchor="w", text_color=("#666666", "#636380"), font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_menu.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="ew")

        # Botón Dashboard (Activo)
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="  Dashboard", anchor="w", fg_color=("#e0e0e0", "#202030"), text_color=("#111111", "white"), hover_color=("#d0d0d0", "#2d2d44"))
        self.btn_dashboard.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.btn_users = ctk.CTkButton(self.sidebar_frame, text="  Users", anchor="w", fg_color="transparent", text_color=("#555555", "#a0a0b0"), hover_color=("#e0e0e0", "#202030"))
        self.btn_users.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        # Sección: Categories
        self.lbl_categories = ctk.CTkLabel(self.sidebar_frame, text="Categories", anchor="w", text_color=("#666666", "#636380"), font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_categories.grid(row=3, column=0, padx=20, pady=(20, 5), sticky="ew")

        categories = ["Stock Measure", "Products", "Manage", "Transactions", "Settings"]
        for i, cat in enumerate(categories):
            btn = ctk.CTkButton(self.sidebar_frame, text=f"  {cat}", anchor="w", fg_color="transparent", text_color=("#555555", "#a0a0b0"), hover_color=("#e0e0e0", "#202030"))
            btn.grid(row=4+i, column=0, padx=15, pady=5, sticky="ew")

        # Sección: Other Links
        self.lbl_other = ctk.CTkLabel(self.sidebar_frame, text="Other Links", anchor="w", text_color=("#666666", "#636380"), font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_other.grid(row=9, column=0, padx=20, pady=(20, 5), sticky="ew")

        self.btn_logout = ctk.CTkButton(self.sidebar_frame, text="  Logout", anchor="w", fg_color="transparent", text_color=("#555555", "#a0a0b0"), hover_color=("#e0e0e0", "#202030"))
        self.btn_logout.grid(row=10, column=0, padx=15, pady=(5, 20), sticky="sw")


        # ==========================================
        # ÁREA PRINCIPAL
        # ==========================================
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # --- Top Bar ---
        self.top_bar = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 10))
        self.top_bar.grid_columnconfigure(1, weight=1)

        self.lbl_title = ctk.CTkLabel(self.top_bar, text="WELCOME ADMIN", font=ctk.CTkFont(size=24, weight="bold"), text_color=("#111111", "white"))
        self.lbl_title.grid(row=0, column=0, sticky="w")

        # Contenedor Buscador
        self.search_frame = ctk.CTkFrame(self.top_bar, fg_color=("#ffffff", "#181824"), corner_radius=8)
        self.search_frame.grid(row=0, column=1, sticky="e", padx=(0, 15))
        
        self.entry_search = ctk.CTkEntry(self.search_frame, placeholder_text="Search", width=250, border_width=0, fg_color="transparent", text_color=("#111111", "white"))
        self.entry_search.pack(padx=10, pady=5)

        # Variable para el tamaño de fuente (escala)
        self.scaling_factor = 1.0

        # Botones de tamaño de fuente (A- y A+)
        self.btn_zoom_out = ctk.CTkButton(self.top_bar, text="A-", width=40, command=self.decrease_font, fg_color=("#ffffff", "#202030"), text_color=("#111111", "white"), hover_color=("#e0e0e0", "#2d2d44"))
        self.btn_zoom_out.grid(row=0, column=2, padx=(0, 5), sticky="e")

        self.btn_zoom_in = ctk.CTkButton(self.top_bar, text="A+", width=40, command=self.increase_font, fg_color=("#ffffff", "#202030"), text_color=("#111111", "white"), hover_color=("#e0e0e0", "#2d2d44"))
        self.btn_zoom_in.grid(row=0, column=3, padx=(0, 15), sticky="e")

        # Botón Tema (Sol/Luna)
        self.btn_theme = ctk.CTkButton(self.top_bar, text="🌙 Oscuro", width=100, command=self.toggle_theme, fg_color=("#ffffff", "#202030"), text_color=("#111111", "white"), hover_color=("#e0e0e0", "#2d2d44"))
        self.btn_theme.grid(row=0, column=4, sticky="e")

        # --- Dashboard View ---
        self.dashboard_view = DashboardView(self.main_container)
        self.dashboard_view.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))

    def toggle_theme(self):
        # Lee el modo actual de CustomTkinter y lo invierte
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("light")
            self.btn_theme.configure(text="🌙 Oscuro")
        else:
            ctk.set_appearance_mode("dark")
            self.btn_theme.configure(text="☀️ Claro")

    def increase_font(self):
        if self.scaling_factor < 2.0:
            self.scaling_factor += 0.1
            ctk.set_widget_scaling(self.scaling_factor)

    def decrease_font(self):
        if self.scaling_factor > 0.6:
            self.scaling_factor -= 0.1
            ctk.set_widget_scaling(self.scaling_factor)
