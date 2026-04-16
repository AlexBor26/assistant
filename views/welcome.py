import flet as ft
from storage.config import save_keys

def welcome_screen(page: ft.Page, on_success):
    """Экран приветствия и ввода API-ключей"""
    
    # Поля для ввода
    weather_key_input = ft.TextField(
        label="OpenWeatherMap API Key",
        width=400,
        password=True
    )
    
    openrouter_key_input = ft.TextField(
        label="OpenRouter API Key (пока можно оставить пустым)", 
        width=400,
        password=True
    )
    
    status = ft.Text("", color=ft.Colors.RED)
    
    def save_clicked(e):
        print("=== save_clicked called ===")
        weather = weather_key_input.value
        openrouter = openrouter_key_input.value or ""
        
        if not weather:
            status.value = "❌ OpenWeatherMap ключ обязателен!"
            page.update()
            return
            
        save_keys(weather, openrouter)
        status.value = "✅ Ключи сохранены!"
        page.update()
        
        print("Calling on_success...")
        on_success()
        print("on_success finished")
    
    save_button = ft.FilledButton("Сохранить и продолжить", on_click=save_clicked)
    
    # Собираем страницу
    page.controls.clear()
    page.add(
        ft.Column(
            [
                ft.Text("Добро пожаловать в Ассистент!", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Для работы нужен API-ключ OpenWeatherMap:", size=14),
                ft.Text("Получить ключ: openweathermap.org/api", size=12, color=ft.Colors.BLUE),
                ft.Divider(),
                weather_key_input,
                openrouter_key_input,
                status,
                save_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )
    page.update()