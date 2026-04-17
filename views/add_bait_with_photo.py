import flet as ft
import os
import shutil
import json
import hashlib
from datetime import datetime
from PIL import Image
from storage.database import add_bait
from services.vision import analyze_bait_image
from storage.config import load_keys

analysis_cache = {}

def get_file_hash(filepath):
    stat = os.stat(filepath)
    data = f"{filepath}_{stat.st_size}_{stat.st_mtime}".encode()
    return hashlib.md5(data).hexdigest()

def compress_image(src_path, max_size=800, quality=85):
    try:
        with Image.open(src_path) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            temp_dir = "assets/temp"
            os.makedirs(temp_dir, exist_ok=True)
            compressed_path = os.path.join(temp_dir, f"compressed_{int(datetime.now().timestamp())}.jpg")
            img.save(compressed_path, "JPEG", quality=quality)
            return compressed_path
    except Exception as e:
        print(f"Ошибка сжатия: {e}")
        return None

def add_bait_with_photo_screen(page: ft.Page, on_back):
    selected_photo_path = None
    photo_preview = ft.Image(width=200, height=200, visible=False)
    
    name_input = ft.TextField(label="Название насадки*", width=400)
    bait_type_input = ft.TextField(label="Тип", width=200)
    flavor_input = ft.TextField(label="Аромат", width=200)
    manufacturer_input = ft.TextField(label="Производитель", width=200)
    season_input = ft.TextField(label="Сезон", width=200)
    notes_input = ft.TextField(label="Заметки", width=400, multiline=True)
    status_text = ft.Text("", color=ft.Colors.BLUE)

    BAITS_DIR = os.path.join(os.path.dirname(__file__), "data", "baits")
    os.makedirs(BAITS_DIR, exist_ok=True)

    def on_camera_image(e):
        nonlocal selected_photo_path
        if e and e.files:
            selected_photo_path = e.files[0].path
            photo_preview.src = selected_photo_path
            photo_preview.visible = True
            status_text.value = "✅ Фото сделано, анализирую..."
            page.update()
            # Автоматически запускаем анализ
            analyze_photo_auto()

    def take_photo(e):
        try:
            file_picker = ft.FilePicker(on_result=on_camera_image)
            page.overlay.append(file_picker)
            file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
        except Exception as ex:
            status_text.value = f"❌ Ошибка камеры: {ex}"
            page.update()

    def save_photo_safely(src_path: str) -> str:
        filename = f"bait_{int(datetime.now().timestamp())}.jpg"
        dst_path = os.path.join(BAITS_DIR, filename)
        with open(src_path, 'rb') as src, open(dst_path, 'wb') as dst:
            dst.write(src.read())
        return dst_path

    def save_bait(e):
        if not name_input.value.strip():
            status_text.value = "❌ Введите название"
            page.update()
            return
        
        saved_photo_path = None
        if selected_photo_path and os.path.exists(selected_photo_path):
            try:
                saved_photo_path = save_photo_safely(selected_photo_path)
            except Exception as ex:
                status_text.value = f"❌ Ошибка сохранения фото: {ex}"
                page.update()
                return

        add_bait(
            name=name_input.value.strip(),
            bait_type=bait_type_input.value.strip(),
            flavor=flavor_input.value.strip(),
            manufacturer=manufacturer_input.value.strip(),
            season=season_input.value.strip(),
            water_temp="",
            color="",
            notes=notes_input.value.strip(),
            photo_path=saved_photo_path
        )
        
        status_text.value = "✅ Насадка добавлена!"
        name_input.value = ""
        bait_type_input.value = ""
        flavor_input.value = ""
        manufacturer_input.value = ""
        season_input.value = ""
        notes_input.value = ""
        photo_preview.visible = False
        selected_photo_path = None
        page.update()

    def analyze_photo_auto():
        nonlocal selected_photo_path
        if not selected_photo_path:
            status_text.value = "❌ Нет фото для анализа"
            page.update()
            return

        status_text.value = "🖼️ Сжатие фото..."
        page.update()
        compressed = compress_image(selected_photo_path)
        if not compressed:
            status_text.value = "❌ Ошибка сжатия"
            page.update()
            return

        file_hash = get_file_hash(selected_photo_path)
        if file_hash in analysis_cache:
            analysis = analysis_cache[file_hash]
            status_text.value = "♻️ Использую кэш"
        else:
            status_text.value = "🤖 Анализирую через ИИ..."
            page.update()
            _, openrouter_key = load_keys()
            if not openrouter_key:
                status_text.value = "❌ Нет ключа OpenRouter"
                page.update()
                return
            analysis = analyze_bait_image(compressed, openrouter_key)
            analysis_cache[file_hash] = analysis

        try:
            os.remove(compressed)
        except:
            pass

        def close_advice():
            advice.open = False
            page.overlay.remove(advice)
            page.update()
            continue_parsing()

        advice = ft.AlertDialog(
            title=ft.Text("🎣 Совет наставника", size=20),
            content=ft.Container(content=ft.Text(analysis, size=13, selectable=True), width=500, height=400, padding=15),
            actions=[ft.TextButton("Продолжить", on_click=lambda e: close_advice())],
        )
        page.overlay.append(advice)
        advice.open = True
        page.update()

        def continue_parsing():
            try:
                start = analysis.find('{')
                end = analysis.rfind('}') + 1
                if start != -1 and end != 0:
                    data = json.loads(analysis[start:end])
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
    camera_button = ft.FilledButton("📷 Снять фото", on_click=take_photo)
    save_button = ft.FilledButton("💾 Сохранить", on_click=save_bait)

    page.controls.clear()
    page.add(
        ft.Column([
            ft.Container(height=40),
            back_button,
            ft.Text("Добавить насадку", size=28),
            camera_button,
            photo_preview,
            name_input,
            ft.Row([bait_type_input, flavor_input], wrap=True),
            ft.Row([manufacturer_input, season_input], wrap=True),
            notes_input,
            save_button,
            status_text,
        ], spacing=15, scroll=ft.ScrollMode.AUTO)
    )
    page.update()
