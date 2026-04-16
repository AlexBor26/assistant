import flet as ft
from storage.database import get_all_reports, get_report_by_id
from storage.database import get_bait_by_id

def reports_screen(page: ft.Page, on_back):
    """Экран истории рыбалок"""
    
    reports_list = ft.Column(spacing=10)
    
    def refresh_reports():
        reports_list.controls.clear()
        reports = get_all_reports()
        
        if not reports:
            reports_list.controls.append(
                ft.Text("Нет сохранённых отчётов", color=ft.Colors.GREY, size=14)
            )
        else:
            for report in reports:
                report_card = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(report["date"][:16], weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(report["location_name"], size=16),
                            ft.Text(f"Клёв: {report['bite_score']}/5, Улов: {report['catch_count']} шт.", size=12),
                        ], spacing=3, expand=True),
                        ft.FilledButton(
                            "Подробнее",
                            on_click=lambda e, rid=report["id"]: show_report_details(rid),
                            style=ft.ButtonStyle(color=ft.Colors.BLUE)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=10,
                    margin=ft.margin.only(bottom=5)
                )
                reports_list.controls.append(report_card)
        
        page.update()
    
    def show_report_details(report_id):
        print(f"=== show_report_details вызван для ID: {report_id} ===")
        
        report = get_report_by_id(report_id)
        if not report:
            print(f"Отчёт с ID {report_id} не найден")
            return
        
        print(f"Отчёт найден: {report['location_name']}")
        
        # Получаем названия насадок
        bait_names = []
        if report.get("bait_ids"):
            bait_ids = report["bait_ids"].split(",")
            for bid in bait_ids:
                if bid:
                    bait = get_bait_by_id(int(bid))
                    if bait:
                        bait_names.append(bait["name"])
        
        bait_text = ", ".join(bait_names) if bait_names else "не указаны"
        
        details_text = f"""
Дата: {report['date']}
Место: {report['location_name']}
Координаты: {report['latitude']}, {report['longitude']}

Погода:
  Температура: {report['weather_temp']}°C
  Ветер: {report['weather_wind']} м/с
  Давление: {report['weather_pressure']} мм
  {report['weather_description']}

Луна: {report['moon_phase']}
Прогноз клёва: {report['bite_score']}/5

Насадки: {bait_text}

Улов: {report['catch_count']} шт.
Вес: {report['catch_weight']} кг
Заметки: {report['notes'] or 'нет'}
"""
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Детали отчёта"),
            content=ft.Container(
                content=ft.Text(details_text, size=12),
                width=400,
                height=450,
                padding=10
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=close_dialog),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
        print("Диалог открыт")
    
    back_button = ft.TextButton("← Назад", on_click=lambda e: on_back())
    refresh_button = ft.TextButton("Обновить", on_click=lambda e: refresh_reports())
    
    refresh_reports()
    
    # Собираем страницу
    page.controls.clear()
    
    main_content = ft.Column(
        [
            ft.Row([back_button, refresh_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("Мои рыбалки", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Container(
                content=reports_list,
                height=500,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                padding=10
            ),
        ],
        spacing=15,
        scroll=ft.ScrollMode.AUTO
    )
    
    page.add(
        ft.Container(
            content=main_content,
            expand=True,
            padding=10
        )
    )
    page.update()