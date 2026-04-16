import json
import os

CONFIG_FILE = "config.json"

def save_keys(weather_key: str, openrouter_key: str):
    """Сохраняет API-ключи в файл"""
    data = {
        "weather_api_key": weather_key,
        "openrouter_api_key": openrouter_key
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)
    print(f"Ключи сохранены в {CONFIG_FILE}")

def load_keys():
    """Загружает API-ключи из файла, если они есть"""
    if not os.path.exists(CONFIG_FILE):
        print("Файл config.json не найден")
        return None, None
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    weather_key = data.get("weather_api_key")
    openrouter_key = data.get("openrouter_api_key")
    print(f"Загружены ключи: weather={'есть' if weather_key else 'нет'}, openrouter={'есть' if openrouter_key else 'нет'}")
    return weather_key, openrouter_key

def save_openrouter_key(key: str):
    """Сохраняет только OpenRouter ключ"""
    weather_key, _ = load_keys()
    save_keys(weather_key or "", key)

def save_weather_key(key: str):
    """Сохраняет только Weather ключ"""
    _, openrouter_key = load_keys()
    save_keys(key, openrouter_key or "")