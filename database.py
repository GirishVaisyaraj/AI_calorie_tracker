import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect("nutrition.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            total_calories REAL,
            total_protein_g REAL,
            total_fat_g REAL,
            total_carbs_g REAL,
            total_fiber_g REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id INTEGER,
            name TEXT,
            estimated_weight REAL,
            calories REAL,
            protein_g REAL,
            fat_g REAL,
            carbs_g REAL,
            total_fiber_g REAL,
            FOREIGN KEY (meal_id) REFERENCES meals (id)
        )
    """)
    conn.commit()
    conn.close()

def add_meal(meal_summary, dishes):
    conn = sqlite3.connect("nutrition.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO meals (date, total_calories, total_protein_g, total_fat_g, total_carbs_g, total_fiber_g)
        VALUES (datetime('now'), ?, ?, ?, ?, ?)
    """, (meal_summary['total_calories'], meal_summary['total_protein_g'], meal_summary['total_fat_g'], meal_summary['total_carbs_g'], meal_summary['total_fiber_g']))
    meal_id = c.lastrowid
    for dish in dishes:
        c.execute("""
            INSERT INTO dishes (meal_id, name, estimated_weight, calories, protein_g, fat_g, carbs_g, total_fiber_g)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (meal_id, dish['name'], dish['estimated_weight'], dish['calories'], dish['protein_g'], dish['fat_g'], dish['carbs_g'], dish['total_fiber_g']))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect("nutrition.db")
    df = pd.read_sql_query("SELECT * FROM meals", conn)
    conn.close()
    return df
