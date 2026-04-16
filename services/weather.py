import requests

def get_weather(lat, lon, api_key):
    """
    Получает погоду по координатам
    
    lat, lon — координаты места рыбалки
    api_key — ключ OpenWeatherMap
    
    Возвращает словарь с данными или None в случае ошибки
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "lang": "ru"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        weather = {
            "temperature": data["main"]["temp"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "wind_deg": data["wind"].get("deg", 0),
            "description": data["weather"][0]["description"],
            "clouds": data["clouds"]["all"]
        }
        
        return weather
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса погоды: {e}")
        return None

def wind_direction(degrees: int) -> str:
    """Переводит градусы в название направления ветра"""
    directions = [
        "С", "СВ", "В", "ЮВ",
        "Ю", "ЮЗ", "З", "СЗ"
    ]
    idx = round(degrees / 45) % 8
    return directions[idx]