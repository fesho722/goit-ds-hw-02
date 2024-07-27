import sqlite3
from faker import Faker

# Підключення до бази даних SQLite
conn = sqlite3.connect('task_management.db')
cursor = conn.cursor()

# Ініціалізація Faker
fake = Faker()

# Заповнення таблиці status
statuses = [('new',), ('in progress',), ('completed',)]
cursor.executemany('INSERT INTO status (name) VALUES (?)', statuses)

# Заповнення таблиці users випадковими даними
for _ in range(10):
    fullname = fake.name()
    email = fake.unique.email()
    cursor.execute('INSERT INTO users (fullname, email) VALUES (?, ?)', (fullname, email))

# Заповнення таблиці tasks випадковими даними
for _ in range(30):
    title = fake.sentence(nb_words=6)
    description = fake.text()
    status_id = fake.random_int(min=1, max=3)
    user_id = fake.random_int(min=1, max=10)
    cursor.execute('INSERT INTO tasks (title, description, status_id, user_id) VALUES (?, ?, ?, ?)', (title, description, status_id, user_id))

# Збереження змін
conn.commit()

# Функції для виконання запитів

def get_tasks_by_user(user_id):
    cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
    return cursor.fetchall()

def get_tasks_by_status(status_name):
    cursor.execute('''
    SELECT * FROM tasks WHERE status_id = (
        SELECT id FROM status WHERE name = ?
    )
    ''', (status_name,))
    return cursor.fetchall()

def update_task_status(task_id, new_status):
    cursor.execute('''
    UPDATE tasks SET status_id = (
        SELECT id FROM status WHERE name = ?
    ) WHERE id = ?
    ''', (new_status, task_id))
    conn.commit()

def get_users_without_tasks():
    cursor.execute('''
    SELECT * FROM users WHERE id NOT IN (
        SELECT DISTINCT user_id FROM tasks
    )
    ''')
    return cursor.fetchall()

def add_task_for_user(title, description, status_name, user_id):
    cursor.execute('''
    INSERT INTO tasks (title, description, status_id, user_id) 
    VALUES (?, ?, (SELECT id FROM status WHERE name = ?), ?)
    ''', (title, description, status_name, user_id))
    conn.commit()

def get_incomplete_tasks():
    cursor.execute('''
    SELECT * FROM tasks WHERE status_id != (
        SELECT id FROM status WHERE name = 'completed'
    )
    ''')
    return cursor.fetchall()

def delete_task(task_id):
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()

def find_users_by_email_pattern(email_pattern):
    cursor.execute('SELECT * FROM users WHERE email LIKE ?', (email_pattern,))
    return cursor.fetchall()

def update_user_name(user_id, new_name):
    cursor.execute('UPDATE users SET fullname = ? WHERE id = ?', (new_name, user_id))
    conn.commit()

def count_tasks_by_status():
    cursor.execute('''
    SELECT s.name, COUNT(t.id) 
    FROM tasks t 
    JOIN status s ON t.status_id = s.id 
    GROUP BY s.name
    ''')
    return cursor.fetchall()

def get_tasks_by_email_domain(domain):
    cursor.execute('''
    SELECT t.* 
    FROM tasks t 
    JOIN users u ON t.user_id = u.id 
    WHERE u.email LIKE ?
    ''', ('%' + domain,))
    return cursor.fetchall()

def get_tasks_without_description():
    cursor.execute('SELECT * FROM tasks WHERE description IS NULL OR description = ""')
    return cursor.fetchall()

def get_users_and_tasks_in_progress():
    cursor.execute('''
    SELECT u.fullname, t.* 
    FROM tasks t 
    JOIN users u ON t.user_id = u.id 
    WHERE t.status_id = (
        SELECT id FROM status WHERE name = 'in progress'
    )
    ''')
    return cursor.fetchall()

def get_user_task_counts():
    cursor.execute('''
    SELECT u.fullname, COUNT(t.id) 
    FROM users u 
    LEFT JOIN tasks t ON u.id = t.user_id 
    GROUP BY u.fullname
    ''')
    return cursor.fetchall()

# Закриття з'єднання
conn.close()
