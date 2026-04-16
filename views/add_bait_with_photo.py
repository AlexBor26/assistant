import flet as ft
import os
import shutil
import json
from datetime import datetime
from storage.database import add_bait
from services.vision import analyze_bait_image
from storage.config import load_keys

def add_bait_with_photo_screen(page: ft.Page, on_back):
    """Экран добавления насадки с фото"""
    
    selected_photo_path = None
    image_preview = ft.Image(src="", width=200, height=200, visible=False)
    photo_path_input = ft.TextField(label="Путь к фото (или выберите ниже)", width=400, read_only=True)
    
    name_input = ft.TextField(label="Название насадки *", width=400)
    bait_type_input = ft.TextField(label="Тип (тесто/сухая смесь/жидкость)", width=200)
    flavor_input = ft.TextField(label="Аромат", width=200)
    manufacturer_input = ft.TextField(label="Производитель", width=200)
    season_input = ft.TextField(label="Сезон", width=200)
    water_temp_input = ft.TextField(label="Температура воды", width=200)
    color_input = ft.TextField(label="Цвет", width=200)
    notes_input = ft.TextField(label="Заметки", width=400, multiline=True)
    
    status_text = ft.Text("", color=ft.Colors.BLUE)
    
    # Файловый пикер
    file_picker = ft.FilePicker(on_result=lambda e: on_file_picked(e))
    page.overlay.append(file_picker)
    
    def on_file_picked(result):
        nonlocal selected_photo_path
        if result and result.files:
            selected_photo_path = result.files[0].path
            photo_path_input.value = selected_photo_path
            image_preview.src = selected_photo_path
            image_preview.visible = True
            status_text.value = f"✅ Фото выбрано: {os.path.basename(selected_photo_path)}"
            page.update()
    
    def pick_photo(e):
        file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
    
    def save_bait(e):
        if not name_input.value:
            status_text.value = "❌ Введите название насадки"
            page.update()
            return
        
        saved_photo_path = None
        if selected_photo_path and os.path.exists(selected_photo_path):
            os.makedirs("assets/baits", exist_ok=True)
            filename = f"bait_{int(datetime.now().timestamp())}.jpg"
            saved_photo_path = f"assets/baits/{filename}"
            shutil.copy2(selected_photo_path, saved_photo_path)
        
        add_bait(
            name=name_input.value,
            bait_type=bait_type_input.value,
            flavor=flavor_input.value,
            manufacturer=manufacturer_input.value,
            season=season_input.value,
            water_temp=water_temp_input.value,
            color=color_input.value,
            notes=notes_input.value,
            photo_path=saved_photo_path
        )
        
        status_text.value = "✅ Насадка добавлена!"
        name_input.value = ""
        bait_type_input.value = ""
        flavor_input.value = ""
        manufacturer_input.value = ""
        season_input.value = ""
        water_temp_input.value = ""
        color_input.value = ""
        notes_input.value = ""
        photo_path_input.value = ""
        image_preview.visible = False
        selected_photo_path = None
        page.update()
    
    def analyze_photo(e):
        nonlocal selected_photo_path
        if not selected_photo_path:
            status_text.value = "❌ Сначала выберите фото"
            page.update()
            return
        
        status_text.value = "🤖 Анализирую фото через ИИ..."
        page.update()
        
        _, openrouter_key = load_keys()
        
        if not openrouter_key:
            status_text.value = "❌ Нет API-ключа OpenRouter"
            page.update()
            return
        
        analysis = analyze_bait_image(selected_photo_path, openrouter_key)
        
        # Диалог с советом от ИИ
        def close_advice_dialog():
            advice_dialog.open = False
            if advice_dialog in page.overlay:
                page.overlay.remove(advice_dialog)
            page.update()
            continue_with_parsing()
        
        advice_dialog = ft.AlertDialog(
            title=ft.Text("🎣 Совет наставника", size=20),
            content=ft.Container(
                content=ft.Text(analysis, size=13, selectable=True),
                width=550,
                height=450,
                padding=15
            ),
            actions=[
                ft.TextButton("Продолжить", on_click=lambda e: close_advice_dialog()),
            ],
        )
        
        page.overlay.append(advice_dialog)
        advice_dialog.open = True
        page.update()
        
        def continue_with_parsing():
            try:
                json_start = analysis.find('{')
                json_end = analysis.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = analysis[json_start:json_end]
                    data = json.loads(json_str)
                    
                    if data.get("name"):
                        name_input.value = data.get("name")
                    if data.get("bait_type"):
                        bait_type_input.value = data.get("bait_type")
                    if data.get("flavor"):
                        flavor_input.value = data.get("flavor")
                    if data.get("brand"):
                        manufacturer_input.value = data.get("brand")
                    if data.get("season"):
                        season_input.value = data.get("season")
                    if data.get("water_temp"):
                        water_temp_input.value = data.get("water_temp")
                    if data.get("color"):
                        color_input.value = data.get("color")
                    
                    notes_lines = []
                    if data.get("target_fish"):
                        notes_lines.append(f"Целевая рыба: {data.get('target_fish')}")
                    if data.get("weight"):
                        notes_lines.append(f"Вес: {data.get('weight')}")
                    if notes_lines:
                        notes_input.value = "\n".join(notes_lines)
                    
                    # Диалог редактирования
                    name_field = ft.TextField(label="Название", value=name_input.value, width=400)
                    type_field = ft.TextField(label="Тип", value=bait_type_input.value, width=400)
                    flavor_field = ft.TextField(label="Аромат", value=flavor_input.value, width=400)
                    brand_field = ft.TextField(label="Производитель", value=manufacturer_input.value, width=400)
                    season_field = ft.TextField(label="Сезон", value=season_input.value, width=400)
                    temp_field = ft.TextField(label="Температура воды", value=water_temp_input.value, width=400)
                    color_field = ft.TextField(label="Цвет", value=color_input.value, width=400)
                    notes_field = ft.TextField(label="Заметки", value=notes_input.value, width=400, multiline=True)
                    
                    def save_from_dialog(e):
                        name_input.value = name_field.value
                        bait_type_input.value = type_field.value
                        flavor_input.value = flavor_field.value
                        manufacturer_input.value = brand_field.value
                        season_input.value = season_field.value
                        water_temp_input.value = temp_field.value
                        color_input.value = color_field.value
                        notes_input.value = notes_field.value
                        
                        try:
                            saved_photo_path = None
                            if selected_photo_path and os.path.exists(selected_photo_path):
                                os.makedirs("assets/baits", exist_ok=True)
                                filename = f"bait_{int(datetime.now().timestamp())}.jpg"
                                saved_photo_path = f"assets/baits/{filename}"
                                shutil.copy2(selected_photo_path, saved_photo_path)
                            
                            add_bait(
                                name=name_input.value,
                                bait_type=bait_type_input.value,
                                flavor=flavor_input.value,
                                manufacturer=manufacturer_input.value,
                                season=season_input.value,
                                water_temp=water_temp_input.value,
                                color=color_input.value,
                                notes=notes_input.value,
                                photo_path=saved_photo_path
                            )
                            status_text.value = "✅ Насадка сохранена!"
                            edit_dialog.open = False
                            page.overlay.remove(edit_dialog)
                            page.update()
                        except Exception as save_err:
                            status_text.value = f"⚠️ Ошибка: {save_err}"
                            page.update()
                    
                    def close_edit_dialog(e):
                        edit_dialog.open = False
                        page.overlay.remove(edit_dialog)
                        page.update()
                    
                    edit_dialog = ft.AlertDialog(
                        title=ft.Text("Редактирование насадки", size=18),
                        content=ft.Column([
                            name_field, type_field, flavor_field, brand_field,
                            season_field, temp_field, color_field, notes_field
                        ], spacing=12, height=450, scroll=ft.ScrollMode.AUTO),
                        actions=[
                            ft.TextButton("Отмена", on_click=close_edit_dialog),
                            ft.FilledButton("Сохранить", on_click=save_from_dialog),
                        ],
                    )
                    
                    page.overlay.append(edit_dialog)
                    edit_dialog.open = True
                    page.update()
                else:
                    status_text.value = "⚠️ Не удалось найти JSON в ответе ИИ"
                    page.update()
            except json.JSONDecodeError as e:
                status_text.value = f"⚠️ Ошибка разбора JSON: {e}"
                page.update()
            except Exception as e:
                status_text.value = f"⚠️ Ошибка: {e}"
                page.update()
    
    back_button = ft.TextButton("← Назад", on_click=lambda e: on_back())
    pick_button = ft.FilledButton("📷 Выбрать фото", on_click=pick_photo)
    save_button = ft.FilledButton("💾 Сохранить насадку", on_click=save_bait)
    analyze_button = ft.FilledButton("🤖 Распознать через ИИ", on_click=analyze_photo)
    
    page.controls.clear()
    page.add(
        ft.ListView(
            [
                back_button,
                ft.Text("Добавить насадку с фото", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                pick_button,
                image_preview,
                photo_path_input,
                ft.Row([save_button, analyze_button], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                ft.Divider(),
                ft.Text("Или заполните вручную:", size=14, weight=ft.FontWeight.BOLD),
                name_input,
                ft.Row([bait_type_input, flavor_input], wrap=True),
                ft.Row([manufacturer_input, season_input], wrap=True),
                ft.Row([water_temp_input, color_input], wrap=True),
                notes_input,
                status_text,
            ],
            spacing=15,
            expand=True
        )
    )
    page.update()
