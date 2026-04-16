from datetime import date

def get_moon_phase(date_obj=None):
    """
    Рассчитывает фазу луны для заданной даты.
    Если дата не указана — использует сегодняшнюю.
    
    Возвращает название фазы на русском языке.
    """
    if date_obj is None:
        date_obj = date.today()
    
    # Известное новолуние: 6 января 2000 года
    known_new_moon = date(2000, 1, 6)
    
    # Количество дней между датами
    days_diff = (date_obj - known_new_moon).days
    
    # Лунный цикл 29.53 дня
    lunar_cycle = 29.53
    
    # Положение в цикле (от 0 до 1)
    phase_index = (days_diff % lunar_cycle) / lunar_cycle
    
    # Определяем фазу по индексу
    # Новолуние: 0-1% и 99-100%
    if phase_index < 0.02 or phase_index >= 0.98:
        return "новолуние"
    # Молодая луна (растущий серп): 2-23%
    elif phase_index < 0.23:
        return "молодая луна"
    # Первая четверть: 23-27% (центр в 25%)
    elif phase_index < 0.27:
        return "первая четверть"
    # Растущая луна: 27-48%
    elif phase_index < 0.48:
        return "растущая луна"
    # Полнолуние: 48-52% (центр в 50%)
    elif phase_index < 0.52:
        return "полнолуние"
    # Убывающая луна: 52-73%
    elif phase_index < 0.73:
        return "убывающая луна"
    # Последняя четверть: 73-77% (центр в 75%)
    elif phase_index < 0.77:
        return "последняя четверть"
    # Старая луна (убывающий серп): 77-98%
    else:
        return "старая луна"