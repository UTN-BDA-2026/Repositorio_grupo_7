import flet as ft
def main(page: ft.Page):
    try:
        page.add(ft.Text("Hello", style=ft.TextThemeStyle.TITLE_LARGE))
        print("SUCCESS")
    except Exception as e:
        print("ERROR:", e)
ft.app(target=main)
