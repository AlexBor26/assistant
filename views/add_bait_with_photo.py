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
    
    photo_path_input = ft.TextField(
        label="Путь к фото", 
        width=400, 
        hint_text="/storage/emulated/0/DCIM/Camera/photo.jpg"
    )
    
    name_input = ft.TextField(label="Название насадки *", width=400)
    bait_type_input = ft.TextField(label="Тип", width=200)
    flavor_input = ft.TextField(label="Аромат", width=200)
    manufacturer_input = ft.TextField(label="Производитель", width=200)
    season_input = ft.TextField(label="Сезон", width=200)
    notes_input = ft.TextField(label="Заметки", width=400, multiline=True)
    
    status_text = ft.Text("", color=ft.Colors.BLUE)
    
    def save_bait(e):
        if not name_input.value:
            status_text.value = "❌ Введите название"
            page.update()
            return
        
        saved_photo_path = None
        photo_path = photo_path_input.value
        if photo_path and os.path.exists(photo_path):
            os.makedirs("assets/baits", exist_ok=True)
            filename = f"bait_{int(datetime.now().timestamp())}.jpg"
            saved_photo_path = f"assets/baits/{filename}"
            shutil.copy2(photo_path, saved_photo_path)
            status_text.value = f"✅ Фото скопировано"
        elif photo_path:
            status_text.value = "⚠️ Файл не найден, проверьте путь"
            page.update()
            return
        
        add_bait(
            name=name_input.value,
            bait_type=bait_type_input.value,
            flavor=flavor_input.value,
            manufacturer=manufacturer_input.value,
            season=season_input.value,
            water_temp="",
            color="",
            notes=notes_input.value,
            photo_path=saved_photo_path
        )
        
        status_text.value = "✅ Насадка добавлена!"
        name_input.value = ""
        bait_type_input.value = ""
        flavor_input.value = ""
        manufacturer_input.value = ""
        season_input.value = ""
        notes_input.value = ""
        photo_path_input.value = ""
        page.update()
    
    def analyze_photo(e):
        photo_path = photo_path_input.value
        if not photo_path:
            status_text.value = "❌ Введите путь к фото"
            page.update()
            return
        
        if not os.path.exists(photo_path):
            status_text.value = "❌ Файл не найден"
            page.update()
            return
        
        status_text.value = "🤖 Анализирую..."
        page.update()
        
        _, openrouter_key = load_keys()
        if not openrouter_key:
            status_text.value = "❌ Нет ключа OpenRouter"
            page.update()
            return
        
        analysis = analyze_bait_image(photo_path, openrouter_key)
        
        def close_advice_dialog():
            advice_dialog.open = False
            page.overlay.remove(advice_dialog)
            page.update()
            continue_with_parsing()
        
        advice_dialog = ft.AlertDialog(
            title=ft.Text("🎣 Совет", size=20),
            content=ft.Container(content=ft.Text(analysis, size=13, selectable=True), width=500, height=400, padding=15),
            actions=[ft.TextButton("Продолжить", on_click=lambda e: close_advice_dialog())],
        )
        page.overlay.append(advice_dialog)
        advice_dialog.open = True
        page.update()
        
        def continue_with_parsing():
            try:
                json_start = analysis.find('{')
                json_end = analysis.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    data = json.loads(analysis[json_start:json_end])
                    if data.get("name"): name_input.value = data.get("name")
                    if data.get("bait_type"): bait_type_input.value = data.get("bait_type")
                    if data.get("flavor"): flavor_input.value = data.get("flavor")
                    if data.get("brand"): manufacturer_input.value = data.get("brand")
                    if data.get("season"): season_input.value = data.get("season")
                    if data.get("target_fish"): notes_input.value = f"Целевая рыба: {data.get('target_fish')}"
                    status_text.value = "✅ Поля заполнены. Нажмите 'Сохранить'"
                    page.update()
            except Exception as ex:
                status_text.value = f"⚠️ Ошибка: {ex}"
                page.update()
    
    back_button = ft.TextButton("← Назад", on_click=lambda e: on_back())
    save_button = ft.FilledButton("💾 Сохранить", on_click=save_bait)
    analyze_button = ft.FilledButton("🤖 Распознать", on_click=analyze_photo)
    
    page.controls.clear()
    page.add(
        ft.Column([
            ft.Container(height=40),
            back_button,
            ft.Text("Добавить насадку", size=28),
            ft.Text("Как найти путь к фото:", size=12, color=ft.Colors.GREY),
            ft.Text("1. Откройте фото в галерее → Подробности", size=11, color=ft.Colors.GREY),
            ft.Text("2. Скопируйте полный путь", size=11, color=ft.Colors.GREY),
            ft.Divider(),
            photo_path_input,
            name_input,
            ft.Row([bait_type_input, flavor_input], wrap=True),
            ft.Row([manufacturer_input, season_input], wrap=True),
            notes_input,
            ft.Row([save_button, analyze_button], alignment=ft.MainAxisAlignment.CENTER),
            status_text,
        ], spacing=15, scroll=ft.ScrollMode.AUTO)
    )
    page.update()
