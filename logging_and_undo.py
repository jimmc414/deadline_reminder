# logging_and_undo.py

import sqlite3
import csv

class Logger:
    def __init__(self):
        self.conn = sqlite3.connect('tasks.db')

    def log_completion(self, task_id, comments=''):
        # Logging is handled in Data Persistence Module
        pass

    def undo_last_action(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT task_id FROM task_logs ORDER BY id DESC LIMIT 1
        ''')
        last_log = cursor.fetchone()
        if last_log:
            task_id = last_log[0]
            # Remove log entry
            cursor.execute('DELETE FROM task_logs WHERE id = (SELECT MAX(id) FROM task_logs)')
            # Mark task as not completed
            cursor.execute('''
                UPDATE tasks SET completed = ? WHERE id = ?
            ''', (False, task_id))
            self.conn.commit()
            return True
        return False

    def export_logs_to_csv(self, filename='task_logs.csv'):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM task_logs')
        logs = cursor.fetchall()
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['id', 'task_id', 'completion_date', 'comments']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for log in logs:
                writer.writerow({
                    'id': log[0],
                    'task_id': log[1],
                    'completion_date': log[2],
                    'comments': log[3]
                })
