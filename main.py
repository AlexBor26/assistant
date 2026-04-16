import flet as ft
from storage.config import load_keys
from storage.database import init_db
from views.welcome import welcome_screen
from views.main_screen import main_screen

def main(page: ft.Page):
    init_db()
    page.title = "Ассистент"
    page.window_width = 500
    page.window_height = 700
    
    weather_key, openrouter_key = load_keys()
    
    if weather_key and openrouter_key:
        main_screen(page)
    else:
        welcome_screen(page, lambda: main_screen(page))

ft.app(target=main)

   # page.window_prevent_close = False
   # page.on_close = on_close