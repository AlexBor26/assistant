import flet as ft
from storage.database import get_all_baits, add_bait, delete_bait, get_bait_by_id
from views.add_bait_with_photo import add_bait_with_photo_screen

def baits_screen(page: ft.Page, on_back):
    """Экран управления насадками"""
    
    baits_list = ft.Column(spacing=10)
    selected_baits = {}
    
    def refresh_baits_list():
        baits_list.controls.clear()
        baits = get_all_baits()
        print(f"Загружено насадок из БД: {len(baits)}")
        
        if not baits:
            baits_list.controls.append(
                ft.Text("Нет добавленных насадок", color=ft.Colors.GREY, size=14)
            )
        else:
            for bait in baits:
                checkbox = ft.Checkbox(
                    value=selected_baits.get(bait["id"], False),
                    on_change=lambda e, bid=bait["id"]: on_checkbox_change(bid, e.control.value)
                )
                
                bait_card = ft.Container(
                    content=ft.Row([
                        checkbox,
                        ft.Column([
                            ft.Text(bait["name"], weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"Тип: {bait['bait_type'] or 'не указан'}", size=12),
                            ft.Text(f"Аромат: {bait['flavor'] or 'не указан'}", size=12),
                        ], spacing=3, expand=True),
                        ft.TextButton(
                            "Удалить",
                            on_click=lambda e, bid=bait["id"]: delete_bait_and_refresh(bid),
                            style=ft.ButtonStyle(color=ft.Colors.RED)
                        )
                    ], alignment=ft.MainAxisAlignment.START, spacing=10),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=10,
                    margin=ft.margin.only(bottom=5)
                )
                baits_list.controls.append(bait_card)
        
        page.update()
    
    def on_checkbox_change(bait_id, value):
        selected_baits[bait_id] = value
    
    def delete_bait_and_refresh(bait_id):
        delete_bait(bait_id)
        refresh_baits_list()
    
    def save_selected_baits_and_back():
        from storage.session import save_selected_baits
        selected_ids = [bid for bid, selected in selected_baits.items() if selected]
        save_selected_baits(selected_ids)
        on_back()
    
    name_input = ft.TextField(label="Название насадки *", width=400)
    bait_type_input = ft.TextField(label="Тип (паста/танто/жидкость)", width=400)
    flavor_input = ft.TextField(label="Аромат", width=400)
    manufacturer_input = ft.TextField(label="Производитель", width=400)
    season_input = ft.TextField(label="Сезон", width=400)
    water_temp_input = ft.TextField(label="Температура воды", width=400)
    color_input = ft.TextField(label="Цвет", width=400)
    notes_input = ft.TextField(label="Заметки", width=400, multiline=True)
    
    status_text = ft.Text("", color=ft.Colors.BLUE)
    
    def add_bait_clicked(e):
        if not name_input.value:
            status_text.value = "❌ Введите название насадки"
            page.update()
            return
        
        add_bait(
            name=name_input.value,
            bait_type=bait_type_input.value,
            flavor=flavor_input.value,
            manufacturer=manufacturer_input.value,
            season=season_input.value,
            water_temp=water_temp_input.value,
            color=color_input.value,
            notes=notes_input.value
        )
        
        name_input.value = ""
        bait_type_input.value = ""
        flavor_input.value = ""
        manufacturer_input.value = ""
        season_input.value = ""
        water_temp_input.value = ""
        color_input.value = ""
        notes_input.value = ""
        
        status_text.value = "✅ Насадка добавлена!"
        refresh_baits_list()
        page.update()
    
    add_button = ft.FilledButton("Добавить насадку", on_click=add_bait_clicked)
    select_button = ft.FilledButton("✅ Выбрать для рыбалки", on_click=lambda e: save_selected_baits_and_back())
    back_button = ft.TextButton("← Назад", on_click=lambda e: on_back())
    refresh_button = ft.TextButton("🔄 Обновить", on_click=lambda e: refresh_baits_list())
    # refresh_button убран - обновление будет при каждом входе
    
    def open_add_with_photo(e):
        add_bait_with_photo_screen(page, lambda: baits_screen(page, on_back))
    
    add_photo_button = ft.FilledButton("📷 Добавить с фото", on_click=open_add_with_photo)
    
       # ... все определения функций и кнопок ...
    
    refresh_baits_list()  # <-- вызываем здесь
    
    page.controls.clear()
    page.add(
        ft.ListView(
            [
                ft.Row([back_button, refresh_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text("📦 Мои насадки", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Добавить новую насадку:", size=16, weight=ft.FontWeight.BOLD),
                name_input,
                ft.Row([bait_type_input, flavor_input], wrap=True),
                ft.Row([manufacturer_input, season_input], wrap=True),
                ft.Row([water_temp_input, color_input], wrap=True),
                notes_input,
                add_button,
                add_photo_button,
                status_text,
                ft.Divider(),
                ft.Text("Список насадок:", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=baits_list,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    padding=10
                ),
                select_button,
            ],
            spacing=15,
            height=page.window_height,  # растягиваем на всё окно
            expand=True  # позволяет прокручиваться
        )
    )
    page.update()