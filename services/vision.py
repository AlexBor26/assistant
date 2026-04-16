import base64
import requests
import json
import os

def translate_chinese(text, api_key):
    """Переводит китайский текст на русский через GPT"""
    if not text or text == "неизвестно" or len(text) < 2:
        return text
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Переведи китайский текст на русский язык. Только перевод, без кавычек и пояснений. Текст: {text}"
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.1
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            translated = result["choices"][0]["message"]["content"].strip()
            return translated if translated else text
        return text
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text

def analyze_bait_image(image_path, api_key):
    """
    Отправляет фото насадки в мультимодальную модель OpenRouter
    """
    if not os.path.exists(image_path):
        return f"❌ Файл не найден: {image_path}"

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = """
Ты — эксперт по рыболовным насадкам. Проанализируй это фото упаковки.

Извлеки информацию в формате JSON:
{
    "brand": "производитель (на русском)",
    "name": "название насадки (на русском)",
    "bait_type": "тип (тесто/сухая смесь/гранулы)",
    "flavor": "аромат (например: моллюски, улитка, рыба, сладкий, молочный, чесночный)",
    "season": "сезонность (весна/лето/осень/зима/всесезонная)",
    "target_fish": "целевая рыба (карп/лещ/карась/сазан/универсал)",
    "water_temp": "температура воды (холодная/тёплая/универсал)",
    "color": "цвет насадки (жёлтый/белый/розовый/зелёный/коричневый/красный)"
}

Если информация отсутствует, укажи "неизвестно".

После JSON дай краткие рекомендации по применению на русском языке.
"""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "qwen/qwen2.5-vl-72b-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{img_b64}"
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Пытаемся перевести китайские иероглифы в JSON части
            try:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = content[json_start:json_end]
                    data = json.loads(json_str)
                    
                    # Переводим китайские поля
                    if data.get("name") and data["name"] != "неизвестно" and any('\u4e00' <= c <= '\u9fff' for c in data["name"]):
                        data["name"] = translate_chinese(data["name"], api_key)
                    if data.get("brand") and data["brand"] != "неизвестно" and any('\u4e00' <= c <= '\u9fff' for c in data["brand"]):
                        data["brand"] = translate_chinese(data["brand"], api_key)
                    if data.get("flavor") and data["flavor"] != "неизвестно" and any('\u4e00' <= c <= '\u9fff' for c in data["flavor"]):
                        data["flavor"] = translate_chinese(data["flavor"], api_key)
                    
                    # Собираем обратно
                    new_json = json.dumps(data, ensure_ascii=False)
                    content = new_json + content[json_end:]
            except Exception as e:
                print(f"Ошибка парсинга/перевода: {e}")
            
            return content
        else:
            return f"❌ Ошибка API: {response.status_code}\n{response.text[:300]}"

    except Exception as e:
        return f"❌ Ошибка: {str(e)}"