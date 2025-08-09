# database.py
import sqlite3
from datetime import date

DB_NAME = 'car_data.db'

def init_db():
    """Инициализирует базу данных и создает таблицы, если их нет."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Таблица для записей о заправках
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date DATE NOT NULL,
                odometer INTEGER NOT NULL,
                liters REAL NOT NULL,
                price_per_liter REAL NOT NULL,
                total_cost REAL NOT NULL
            )
        ''')
        # Таблица для записей о замене запчастей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_name TEXT NOT NULL,
                replacement_date DATE NOT NULL,
                replacement_odometer INTEGER NOT NULL,
                price REAL NOT NULL,
                lifespan_km INTEGER,
                notes TEXT
            )
        ''')
        conn.commit()

def add_fuel_record(odometer, liters, price_per_liter):
    """Добавляет запись о заправке в БД."""
    total_cost = round(liters * price_per_liter, 2)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO fuel_log (log_date, odometer, liters, price_per_liter, total_cost) VALUES (?, ?, ?, ?, ?)',
            (date.today(), odometer, liters, price_per_liter, total_cost)
        )
        conn.commit()
    return total_cost

def add_part_record(part_name, odometer, price, lifespan_km=None, notes=''):
    """Добавляет запись о замене запчасти в БД."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO parts_log (part_name, replacement_date, replacement_odometer, price, lifespan_km, notes) VALUES (?, ?, ?, ?, ?, ?)',
            (part_name, date.today(), odometer, price, lifespan_km, notes)
        )
        conn.commit()

def get_latest_odometer():
    """Возвращает последний известный пробег из обеих таблиц."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(odometer) FROM fuel_log')
        last_fuel_odo = cursor.fetchone()[0] or 0
        cursor.execute('SELECT MAX(replacement_odometer) FROM parts_log')
        last_part_odo = cursor.fetchone()[0] or 0
        return max(last_fuel_odo, last_part_odo)

def get_reminders(current_odometer):
    """Проверяет, какие запчасти пора менять."""
    reminders = []
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Выбираем последнюю замену для каждой уникальной запчасти, у которой есть ресурс
        cursor.execute('''
            SELECT part_name, MAX(replacement_odometer), lifespan_km 
            FROM parts_log 
            WHERE lifespan_km IS NOT NULL 
            GROUP BY part_name
        ''')
        parts = cursor.fetchall()

        for part_name, last_odo, lifespan in parts:
            km_since_replacement = current_odometer - last_odo
            if km_since_replacement >= lifespan:
                reminders.append(f"🔴 СРОЧНО ЗАМЕНИТЬ: '{part_name}'. Пробег после замены: {km_since_replacement} км (ресурс {lifespan} км).")
            elif lifespan - km_since_replacement <= 2000: # Напоминание за 2000 км до замены
                 reminders.append(f"🟡 СКОРО ЗАМЕНА: '{part_name}'. Осталось {lifespan - km_since_replacement} км до плановой замены.")
    return reminders

def get_full_analysis():
    """Собирает полную статистику по затратам."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(total_cost) FROM fuel_log')
        total_fuel_cost = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(price) FROM parts_log')
        total_parts_cost = cursor.fetchone()[0] or 0
        
        total_cost = total_fuel_cost + total_parts_cost
        
        return {
            "total_fuel": round(total_fuel_cost, 2),
            "total_parts": round(total_parts_cost, 2),
            "grand_total": round(total_cost, 2),
        }