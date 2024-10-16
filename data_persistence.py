import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('tasks.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                name TEXT,
                due_date TEXT,
                completed BOOLEAN,
                notes TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                completion_date TEXT,
                comments TEXT
            )
        ''')
        self.conn.commit()

    def add_task(self, task_id, name, due_date, notes=''):  # Accept notes as an argument
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO tasks (id, name, due_date, completed, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (task_id, name, due_date, False, notes))  # Add notes when inserting task
        self.conn.commit()

    def get_all_tasks(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task[0],
                'name': task[1],
                'due_date': task[2],
                'completed': task[3],
                'notes': task[4]
            })
        return task_list

    def mark_task_complete(self, task_id, comment):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE tasks SET completed = ? WHERE id = ?
        ''', (True, task_id))
        self.conn.commit()
        # Add to logs
        cursor.execute('''
            INSERT INTO task_logs (task_id, completion_date, comments)
            VALUES (?, DATE('now'), ?)
        ''', (task_id, comment))    
        
    def delete_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        cursor.execute('DELETE FROM task_logs WHERE task_id = ?', (task_id,))
        self.conn.commit()
        self.conn.commit()

    def update_task_due_date(self, task_id, new_due_date):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE tasks SET due_date = ? WHERE id = ?', (new_due_date, task_id))
        self.conn.commit()

    def get_last_completed_date(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT completion_date FROM task_logs
            WHERE task_id = ?
            ORDER BY completion_date DESC
            LIMIT 1
        ''', (task_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def delete_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        cursor.execute('DELETE FROM task_logs WHERE task_id = ?', (task_id,))
        self.conn.commit()