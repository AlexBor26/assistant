def calculate_bite_score(weather: dict, moon_phase: str) -> int:
    """
    Рассчитывает прогноз клёва по шкале 0-5
    
    weather — словарь с данными погоды (температура, давление, ветер)
    moon_phase — фаза луны (например, "полнолуние", "новолуние")
    
    Возвращает число от 0 до 5
    """
    score = 3  # начинаем со среднего значения
    
    # Температура (идеально 15-25°C для херабуны)
    temp = weather["temperature"]
    if 15 <= temp <= 25:
        score += 1
    elif temp < 5 or temp > 30:
        score -= 1
    
    # Давление (оптимально 750-770 мм рт. ст.)
    pressure = weather["pressure"]
    if 750 <= pressure <= 770:
        score += 1
    elif pressure < 730 or pressure > 790:
        score -= 1
    
    # Ветер (слабый ветер лучше, сильный — хуже)
    wind = weather["wind_speed"]
    if wind < 3:
        score += 1
    elif wind > 8:
        score -= 1
    
    # Фаза луны (полнолуние и новолуние считаются плохими для клёва)
    bad_moons = ["полнолуние", "новолуние"]
    if moon_phase in bad_moons:
        score -= 1
    
    # Ограничиваем результат от 0 до 5
    score = max(0, min(5, score))
    
    return score