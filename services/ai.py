import requests
import json

def get_ai_advice(weather_data, moon_phase, selected_baits, location_name, history_reports):
    """
    Запрашивает совет у ИИ через OpenRouter
    """
    try:
        from storage.config import load_keys
        _, api_key = load_keys()
    except Exception as e:
        return f"❌ Ошибка загрузки ключа: {str(e)}"
    
    if not api_key:
        return "❌ API-ключ OpenRouter не найден. Введите его в настройках."
    
    # Формируем промпт
    baits_text = ", ".join([b["name"] for b in selected_baits]) if selected_baits else "не выбраны"
    
    # Формируем историю отчётов (кратко)
    history_text = ""
    if history_reports:
        history_text = "\n\nИстория ваших рыбалок на этом водоёме:\n"
        for r in history_reports[:5]:  # последние 5
            history_text += f"- {r['date'][:10]}: улов {r['catch_count']} шт, клёв {r['bite_score']}/5, насадки: {r['baits']}\n"
    
    prompt = f"""Ты — опытный наставник по ловле рыбы. Дай совет рыбаку.

Место: {location_name}
Погода сейчас:
  Температура: {weather_data['temperature']}°C
  Ветер: {weather_data['wind_speed']} м/с
  Давление: {weather_data['pressure']} мм
  Описание: {weather_data['description']}
Фаза луны: {moon_phase}
Выбранные насадки: {baits_text}
{history_text}

Ответь на русском языке, живым разговорным стилем, как опытный рыбак-наставник. 
Дай конкретные рекомендации:
1. Стоит ли сегодня ехать на рыбалку (прогноз клёва)?
2. Какие насадки лучше использовать из выбранных?
3. Что посоветуешь по тактике ловли?
Будь краток, но полезен. Не более 500 символов."""
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.8,
            }),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"❌ Ошибка API: {response.status_code}\n{response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return "❌ Превышено время ожидания ответа от ИИ. Попробуйте позже."
    except Exception as e:
        return f"❌ Ошибка подключения: {str(e)}"