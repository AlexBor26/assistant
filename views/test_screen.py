import flet as ft

def test_screen(page: ft.Page):
    page.controls.clear()
    page.add(ft.Text("Тестовый экран работает!", size=30, color=ft.Colors.GREEN))
    page.update()