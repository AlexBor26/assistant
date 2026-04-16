import flet as ft
from storage.config import load_keys
from services.weather import get_weather, wind_direction
from services.moon import get_moon_phase
from services.bite_forecast import calculate_bite_score
from views.baits_screen import baits_screen
from views.reports_screen import reports_screen
from storage.database import save_report
from storage.session import load_selected_baits, clear_session

def main_screen(page: ft.Page):
    print("=== main_screen ВЫЗВАНА ===")
    weather_key, openrouter_key = load_keys()
    print(f"Ключ погоды: {weather_key[:10]}...")  # покажем первые 10 символов
    
    location_name = ft.TextField(label="Название водоёма", width=400)
    lat_input = ft.TextField(label="Широта", width=180)
    lon_input = ft.TextField(label="Долгота", width=180)
    
    forecast_button = ft.FilledButton("Получить прогноз")
    print("Элементы ввода созданы")
    
    def open_baits_screen(e):
        baits_screen(page, lambda: main_screen(page))
    baits_button = ft.FilledButton("Мои насадки", on_click=open_baits_screen)
    
    def open_reports_screen(e):
        reports_screen(page, lambda: main_screen(page))
    reports_button = ft.FilledButton("Мои рыбалки", on_click=open_reports_screen)
    
    status_text = ft.Text("", color=ft.Colors.BLUE)
    result_container = ft.Column(spacing=10)
    
    current_weather_data = None
    current_moon_phase = None
    current_bite_score = None
    
    def get_forecast(e):
        nonlocal current_weather_data, current_moon_phase, current_bite_score
        
        if not location_name.value:
            status_text.value = "Введите название водоёма"
            page.update()
            return
        
        try:
            lat = float(lat_input.value)
            lon = float(lon_input.value)
        except ValueError:
            status_text.value = "Введите корректные координаты"
            page.update()
            return
        
        status_text.value = "Получаем погоду..."
        forecast_button.disabled = True
        page.update()
        
        weather = get_weather(lat, lon, weather_key)
        
        if not weather:
            status_text.value = "Ошибка получения погоды"
            forecast_button.disabled = False
            page.update()
            return
        
        moon_phase = get_moon_phase()
        bite_score = calculate_bite_score(weather, moon_phase)
        wind_dir = wind_direction(weather["wind_deg"])
        stars = "⭐" * bite_score + "☆" * (5 - bite_score)
        
        current_weather_data = weather
        current_moon_phase = moon_phase
        current_bite_score = bite_score
        
        selected_bait_ids = load_selected_baits()
        selected_baits_names = []
        for bid in selected_bait_ids:
            from storage.database import get_bait_by_id
            bait = get_bait_by_id(bid)
            if bait:
                selected_baits_names.append(bait["name"])
        
        result_container.controls = [
            ft.Text("=" * 40, size=12),
            ft.Text(location_name.value, size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"Температура: {weather['temperature']}°C"),
            ft.Text(f"Ветер: {wind_dir} {weather['wind_speed']} м/с"),
            ft.Text(f"Давление: {weather['pressure']} мм"),
            ft.Text(f"Небо: {weather['description']}"),
            ft.Divider(),
            ft.Text(f"Луна: {moon_phase}"),
            ft.Divider(),
            ft.Text(f"Прогноз клёва: {bite_score}/5", size=18),
            ft.Text(stars, size=20),
        ]
        
        if selected_baits_names:
            result_container.controls.append(ft.Divider())
            result_container.controls.append(ft.Text("Насадки на сегодня:"))
            for bait_name in selected_baits_names:
                result_container.controls.append(ft.Text(f"  • {bait_name}", size=14))
        
        status_text.value = "Готово"
        forecast_button.disabled = False
        page.update()
    
    def save_report_clicked(e):
        print("=== КНОПКА СОХРАНИТЬ НАЖАТА ===")
        
        if current_weather_data is None:
            print("ОШИБКА: current_weather_data = None")
            status_text.value = "Сначала получите прогноз"
            page.update()
            return
        
        print(f"Погода: {current_weather_data}")
        print(f"Место: {location_name.value}")
        print(f"Координаты: {lat_input.value}, {lon_input.value}")
        print(f"Прогноз клёва: {current_bite_score}")
        
        # Поля для ввода улова
        catch_count_input = ft.TextField(label="Количество рыб", width=200)
        catch_weight_input = ft.TextField(label="Вес (кг)", width=200)
        notes_input = ft.TextField(label="Заметки", width=400, multiline=True)
        
        def do_save(e):
            print("=== СОХРАНЕНИЕ ОТЧЁТА ===")
            
            try:
                catch_count = int(catch_count_input.value or 0)
            except:
                catch_count = 0
            try:
                catch_weight = float(catch_weight_input.value or 0)
            except:
                catch_weight = 0
            
            print(f"Улов: {catch_count} шт, Вес: {catch_weight} кг")
            print(f"Заметки: {notes_input.value}")
            
            selected_bait_ids = load_selected_baits()
            bait_ids_str = ",".join(str(bid) for bid in selected_bait_ids)
            print(f"ID насадок: {bait_ids_str}")
            
            try:
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
                print("ОТЧЁТ УСПЕШНО СОХРАНЁН!")
                clear_session()
                dialog.open = False
                page.update()
                status_text.value = "Отчёт сохранён!"
                page.update()
            except Exception as ex:
                print(f"ОШИБКА ПРИ СОХРАНЕНИИ: {ex}")
                status_text.value = f"Ошибка: {ex}"
                page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Сохранить отчёт"),
            content=ft.Column([
                ft.Text(f"Место: {location_name.value}"),
                ft.Text(f"Прогноз клёва: {current_bite_score}/5"),
                ft.Divider(),
                catch_count_input,
                catch_weight_input,
                notes_input,
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                ft.FilledButton("Сохранить", on_click=do_save),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        print(f"Добавлено элементов в scroll_view: {len(scroll_view.controls)}")
        page.add(scroll_view)
        page.update()
        print("=== main_screen ЗАВЕРШЕНА ===")
        page.update()