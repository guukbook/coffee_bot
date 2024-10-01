import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('quiz_results.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS results
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     user_id INTEGER,
     score INTEGER,
     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

async def save_result(user_id: int, score: int):
    conn = sqlite3.connect('quiz_results.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO results (user_id, score) VALUES (?, ?)', (user_id, score))
    conn.commit()
    conn.close()

async def get_statistics():
    conn = sqlite3.connect('quiz_results.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT user_id, MAX(score) as best_score, COUNT(*) as games_played
    FROM results
    GROUP BY user_id
    ORDER BY best_score DESC
    LIMIT 10
    ''')
    results = cursor.fetchall()
    conn.close()

    if not results:
        return "Пока нет статистики, бро! Будь первым, кто пройдет квиз! 🏄‍♂️"

    stats = "Топ-10 серферов кофейных волн:\n\n"
    for i, (user_id, best_score, games_played) in enumerate(results, 1):
        stats += f"{i}. Серфер {user_id}: лучший счет {best_score}, заездов {games_played} 🌊\n"
    
    return stats

# Инициализация базы данных при импорте модуля
init_db()