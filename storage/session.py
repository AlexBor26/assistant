import json
import os

SESSION_FILE = "current_session.json"

def save_selected_baits(bait_ids):
    """Сохраняет выбранные насадки для текущей рыбалки"""
    data = {
        "selected_baits": bait_ids
    }
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)
    print(f"Сохранены насадки: {bait_ids}")

def load_selected_baits():
    """Загружает выбранные насадки для текущей рыбалки"""
    if not os.path.exists(SESSION_FILE):
        return []
    with open(SESSION_FILE, "r") as f:
        data = json.load(f)
    return data.get("selected_baits", [])

def clear_session():
    """Очищает текущую сессию"""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)