import flet as ft
from storage.config import load_keys
from services.weather import get_weather, wind_direction
from services.moon import get_moon_phase
from services.bite_forecast import calculate_bite_score
from views.baits_screen import baits_screen

def main_screen(page: ft.Page):
    """Основной экран с прогнозом"""
    
    # Загружаем ключи
    weather_key, openrouter_key = load_keys()
    
    # Элементы ввода
    location_name = ft.TextField(
        label="Название водоёма",
        width=400,
        hint_text="например: Городской пруд, Ока, Можайское вдхр"
    )
    
    lat_input = ft.TextField(
        label="Широта",
        width=180,
        hint_text="55.7512"
    )
    
    lon_input = ft.TextField(
        label="Долгота",
        width=180,
        hint_text="37.6184"
    )
    
    # Кнопка прогноза
    forecast_button = ft.FilledButton("Получить прогноз")

    def open_baits_screen(e):
        baits_screen(page, lambda: main_screen(page))

    baits_button = ft.FilledButton("📦 Мои насадки", on_click=open_baits_screen)
    
    # Статус (загрузка, ошибки)
    status_text = ft.Text("", color=ft.Colors.BLUE)
    
    # Контейнер для результатов (будем заполнять после прогноза)
    result_container = ft.Column(spacing=10)
    
    def get_forecast(e):
        """Обработчик нажатия кнопки прогноза"""
        
        # Проверяем название водоёма
        if not location_name.value:
            status_text.value = "❌ Введите название водоёма"
            page.update()
            return
        
        # Проверяем координаты
        try:
            lat = float(lat_input.value)
            lon = float(lon_input.value)
        except ValueError:
            status_text.value = "❌ Введите корректные координаты (числа)"
            page.update()
            return
        
        # Показываем, что идёт загрузка
        status_text.value = "⏳ Получаем погоду..."
        forecast_button.disabled = True
        page.update()
        
        # Запрашиваем погоду
        weather = get_weather(lat, lon, weather_key)
        
        if not weather:
            status_text.value = "❌ Ошибка получения погоды. Проверьте интернет и API-ключ"
            forecast_button.disabled = False
            page.update()
            return
        
        # Получаем фазу луны
        moon_phase = get_moon_phase()
        
        # Рассчитываем прогноз клёва
        bite_score = calculate_bite_score(weather, moon_phase)
        
        # Определяем направление ветра
        wind_dir = wind_direction(weather["wind_deg"])
        
        # Рисуем звёздочки для прогноза
        stars = "⭐" * bite_score + "☆" * (5 - bite_score)
        
        # Заполняем результат
        result_container.controls = [
            ft.Text("=" * 40, size=12),
            ft.Text(f"🌊 {location_name.value}", size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"📍 Координаты: {lat}, {lon}"),
            ft.Divider(),
            ft.Text("🌡 ПОГОДА:", weight=ft.FontWeight.BOLD),
            ft.Text(f"Температура: {weather['temperature']}°C"),
            ft.Text(f"Ветер: {wind_dir} {weather['wind_speed']} м/с"),
            ft.Text(f"Давление: {weather['pressure']} мм рт. ст."),
            ft.Text(f"Небо: {weather['description']}, облачность {weather['clouds']}%"),
            ft.Divider(),
            ft.Text("🌙 ЛУНА:", weight=ft.FontWeight.BOLD),
            ft.Text(f"Фаза: {moon_phase}"),
            ft.Divider(),
            ft.Text("🐟 ПРОГНОЗ КЛЁВА:", size=18, weight=ft.FontWeight.BOLD),
            ft.Text(stars, size=20),
            ft.Text(f"{bite_score} из 5", size=16, color=ft.Colors.GREEN if bite_score >= 3 else ft.Colors.ORANGE),
        ]
        
        # Если луна неблагоприятная — добавляем предупреждение
        if moon_phase in ["новолуние", "полнолуние"]:
            result_container.controls.append(
                ft.Text("⚠️ Внимание: в эту фазу луны клёв может быть хуже", 
                       color=ft.Colors.ORANGE, size=12)
            )
        
        status_text.value = "✅ Готово"
        forecast_button.disabled = False
        page.update()
    
    # Привязываем обработчик к кнопке
    forecast_button.on_click = get_forecast
    
    # Собираем страницу
    page.controls.clear()
    page.add(
        ft.Column(
            [
                ft.Text("🎣 Ассистент рыбака", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("Введите место рыбалки:", size=16),
                location_name,
                ft.Text("Координаты (можно взять в Google Maps):", size=12, color=ft.Colors.GREY),
                ft.Row([lat_input, lon_input], alignment=ft.MainAxisAlignment.CENTER),
                forecast_button,
                baits_button = ft.FilledButton("📦 Мои насадки", on_click=open_baits_screen)
                status_text,
                result_container,
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )
    )
    page.update()