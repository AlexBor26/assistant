import sqlite3
import os

DB_FILE = "assistant.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS baits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bait_type TEXT,
            flavor TEXT,
            manufacturer TEXT,
            season TEXT,
            water_temp TEXT,
            color TEXT,
            notes TEXT,
            photo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            location_name TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            weather_temp REAL,
            weather_wind REAL,
            weather_pressure REAL,
            weather_description TEXT,
            moon_phase TEXT,
            bite_score INTEGER,
            bait_ids TEXT,
            catch_count INTEGER,
            catch_weight REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_bait(name, bait_type=None, flavor=None, manufacturer=None, 
             season=None, water_temp=None, color=None, notes=None, photo_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO baits (name, bait_type, flavor, manufacturer, season, water_temp, color, notes, photo_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, bait_type, flavor, manufacturer, season, water_temp, color, notes, photo_path))
    conn.commit()
    bait_id = cursor.lastrowid
    conn.close()
    return bait_id

def get_all_baits():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, bait_type, flavor, manufacturer, season, water_temp, color, notes, photo_path FROM baits ORDER BY name')
    rows = cursor.fetchall()
    conn.close()
    baits = []
    for row in rows:
        baits.append({
            "id": row[0],
            "name": row[1],
            "bait_type": row[2],
            "flavor": row[3],
            "manufacturer": row[4],
            "season": row[5],
            "water_temp": row[6],
            "color": row[7],
            "notes": row[8],
            "photo_path": row[9]
        })
    return baits

def get_bait_by_id(bait_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, bait_type, flavor, manufacturer, season, water_temp, color, notes, photo_path FROM baits WHERE id = ?', (bait_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "bait_type": row[2],
            "flavor": row[3],
            "manufacturer": row[4],
            "season": row[5],
            "water_temp": row[6],
            "color": row[7],
            "notes": row[8],
            "photo_path": row[9]
        }
    return None

def delete_bait(bait_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM baits WHERE id = ?', (bait_id,))
    conn.commit()
    conn.close()

def save_report(location_name, latitude, longitude, weather_temp, weather_wind,
                weather_pressure, weather_description, moon_phase, bite_score,
                bait_ids, catch_count, catch_weight, notes):
    from datetime import datetime
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reports (
            date, location_name, latitude, longitude,
            weather_temp, weather_wind, weather_pressure, weather_description,
            moon_phase, bite_score, bait_ids, catch_count, catch_weight, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        location_name, latitude, longitude,
        weather_temp, weather_wind, weather_pressure, weather_description,
        moon_phase, bite_score, bait_ids, catch_count, catch_weight, notes
    ))
    conn.commit()
    conn.close()

def get_all_reports():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, date, location_name, weather_temp, bite_score, catch_count, notes FROM reports ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    reports = []
    for row in rows:
        reports.append({
            "id": row[0],
            "date": row[1],
            "location_name": row[2],
            "weather_temp": row[3],
            "bite_score": row[4],
            "catch_count": row[5],
            "notes": row[6]
        })
    return reports

def get_report_by_id(report_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "date": row[1],
            "location_name": row[2],
            "latitude": row[3],
            "longitude": row[4],
            "weather_temp": row[5],
            "weather_wind": row[6],
            "weather_pressure": row[7],
            "weather_description": row[8],
            "moon_phase": row[9],
            "bite_score": row[10],
            "bait_ids": row[11],
            "catch_count": row[12],
            "catch_weight": row[13],
            "notes": row[14]
        }
    return None