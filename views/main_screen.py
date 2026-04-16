import flet as ft
from storage.config import load_keys
from services.weather import get_weather, wind_direction
from services.moon import get_moon_phase
from services.bite_forecast import calculate_bite_score
from views.baits_screen import baits_screen
from views.reports_screen import reports_screen
from storage.database import save_report, get_all_reports
from storage.session import load_selected_baits, clear_session
from services.ai import get_ai_advice

def main_screen(page: ft.Page):
    print("=== main_screen начал работу ===")
    
    weather_key, openrouter_key = load_keys()
    print(f"Ключ получен: {weather_key[:10] if weather_key else 'None'}...")
    
    # Создаём элементы
    title = ft.Text("Ассистент рыбака", size=32, weight=ft.FontWeight.BOLD)
    location_name = ft.TextField(label="Название водоёма", width=400)
    lat_input = ft.TextField(label="Широта", width=180)
    lon_input = ft.TextField(label="Долгота", width=180)
    forecast_button = ft.FilledButton("Получить прогноз")
    status_text = ft.Text("", color=ft.Colors.BLUE)
    result_container = ft.Column(spacing=10)
    
    # Переменные для хранения данных прогноза
    current_weather_data = None
    current_moon_phase = None
    current_bite_score = None
    
    # Кнопка "Мои насадки"
    def open_baits_screen(e):
        baits_screen(page, lambda: main_screen(page))
    
    baits_button = ft.FilledButton("Мои насадки", on_click=open_baits_screen)
    
    # Кнопка "Мои рыбалки"
    def open_reports_screen(e):
        reports_screen(page, lambda: main_screen(page))
    
    reports_button = ft.FilledButton("Мои рыбалки", on_click=open_reports_screen)
    
    def get_location_history(location_name_val):
        """Возвращает историю отчётов для указанного водоёма"""
        reports = get_all_reports()
        history = []
        for r in reports:
            if r["location_name"].lower() == location_name_val.lower():
                from storage.database import get_report_by_id, get_bait_by_id
                full_report = get_report_by_id(r["id"])
                baits_str = ""
                if full_report and full_report.get("bait_ids"):
                    bait_ids = full_report["bait_ids"].split(",")
                    for bid in bait_ids:
                        if bid:
                            bait = get_bait_by_id(int(bid))
                            if bait:
                                baits_str += bait["name"] + ", "
                    baits_str = baits_str.rstrip(", ")
                history.append({
                    "date": r["date"],
                    "catch_count": r["catch_count"],
                    "bite_score": r["bite_score"],
                    "baits": baits_str or "не указаны"
                })
        return history[-10:]
    
    def get_ai_suggestion(e):
        print("=== Запрос к ИИ ===")
        
        if current_weather_data is None:
            status_text.value = "Сначала получите прогноз погоды"
            page.update()
            return
        
        status_text.value = "🤔 Советуюсь с наставником..."
        page.update()
        
        selected_bait_ids = load_selected_baits()
        selected_baits = []
        for bid in selected_bait_ids:
            from storage.database import get_bait_by_id
            bait = get_bait_by_id(bid)
            if bait:
                selected_baits.append(bait)
        
        history = get_location_history(location_name.value)
        
        advice = get_ai_advice(
            current_weather_data,
            current_moon_phase,
            selected_baits,
            location_name.value,
            history
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("🎣 Совет наставника", size=20),
            content=ft.Container(
                content=ft.Text(advice, size=14),
                width=400,
                height=300,
                padding=10
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=lambda e: close_dialog(dialog)),
            ],
        )
        
        def close_dialog(d):
            d.open = False
            if d in page.overlay:
                page.overlay.remove(d)
            page.update()
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
        
        status_text.value = "Готово"
        page.update()
    
    def get_forecast(e):
        nonlocal current_weather_data, current_moon_phase, current_bite_score
        
        print("=== Прогноз нажат ===")
        status_text.value = "Получаем погоду..."
        page.update()
        
        try:
            lat = float(lat_input.value)
            lon = float(lon_input.value)
        except ValueError:
            status_text.value = "Введите координаты"
            page.update()
            return
        
        weather = get_weather(lat, lon, weather_key)
        if not weather:
            status_text.value = "Ошибка погоды"
            page.update()
            return
        
        moon_phase = get_moon_phase()
        bite_score = calculate_bite_score(weather, moon_phase)
        stars = "⭐" * bite_score + "☆" * (5 - bite_score)
        
        current_weather_data = weather
        current_moon_phase = moon_phase
        current_bite_score = bite_score
        
        result_container.controls = [
            ft.Text(f"Температура: {weather['temperature']}°C"),
            ft.Text(f"Ветер: {weather['wind_speed']} м/с"),
            ft.Text(f"Луна: {moon_phase}"),
            ft.Text(f"Прогноз клёва: {bite_score}/5"),
            ft.Text(stars),
        ]
        status_text.value = "Готово"
        page.update()
    
    def save_report_clicked(e):
        print("=== Сохранение отчёта ===")
        
        if current_weather_data is None:
            status_text.value = "Сначала получите прогноз"
            page.update()
            return
        
        catch_count_input = ft.TextField(label="Количество рыб", width=200)
        catch_weight_input = ft.TextField(label="Вес (кг)", width=200)
        notes_input = ft.TextField(label="Заметки", width=400, multiline=True)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Сохранить отчёт"),
            content=ft.Column([
                ft.Text(f"Место: {location_name.value}"),
                ft.Text(f"Прогноз клёва: {current_bite_score}/5"),
                ft.Divider(),
                catch_count_input,
                catch_weight_input,
                notes_input,
            ], tight=True, spacing=10, width=400),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: close_dialog(dialog)),
                ft.FilledButton("Сохранить", on_click=lambda e: save_and_close()),
            ],
        )
        
        def close_dialog(d):
            d.open = False
            if d in page.overlay:
                page.overlay.remove(d)
            page.update()
        
        def save_and_close():
            try:
                catch_count = int(catch_count_input.value or 0)
            except:
                catch_count = 0
            try:
                catch_weight = float(catch_weight_input.value or 0)
            except:
                catch_weight = 0
            
            selected_bait_ids = load_selected_baits()
            bait_ids_str = ",".join(str(bid) for bid in selected_bait_ids)
            
            save_report(
                location_name=location_name.value,
                latitude=float(lat_input.value),
                longitude=float(lon_input.value),
                weather_temp=current_weather_data["temperature"],
                weather_wind=current_weather_data["wind_speed"],
                weather_pressure=current_weather_data["pressure"],
                weather_description=current_weather_data["description"],
                moon_phase=current_moon_phase,
                bite_score=current_bite_score,
                bait_ids=bait_ids_str,
                catch_count=catch_count,
                catch_weight=catch_weight,
                notes=notes_input.value or ""
            )
            clear_session()
            close_dialog(dialog)
            status_text.value = "✅ Отчёт сохранён!"
            page.update()
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    forecast_button.on_click = get_forecast
    
    # Собираем страницу
    page.controls.clear()
    page.add(
        ft.Column([
            title,
            location_name,
            ft.Row([lat_input, lon_input]),
            forecast_button,
            baits_button,
            reports_button,
            ft.FilledButton("Сохранить отчёт", on_click=save_report_clicked),
            ft.FilledButton("🤖 Совет наставника", on_click=get_ai_suggestion),
            status_text,
            result_container,
        ], spacing=15)
    )
    page.update()
    print("=== main_screen завершил работу ===")