import yaml
from data_persistence import Database
from datetime import datetime, timedelta

class TaskManager:
    def __init__(self):
        self.db = Database()
        self.tasks_config = self.load_tasks_config()
        self.tasks = self.load_tasks_from_db()

    def load_tasks_config(self):
        with open('tasks.yaml', 'r') as file:
            return yaml.safe_load(file)['tasks']

    def load_tasks_from_db(self):
        tasks = self.db.get_all_tasks()
        if not tasks:
            # Initialize tasks in the database
            for task in self.tasks_config:
                due_date = self.calculate_due_date(task)
                self.db.add_task(task['id'], task['name'], due_date)
            tasks = self.db.get_all_tasks()
        return tasks

    def reload_tasks(self):
        self.tasks = self.load_tasks_from_db()

    def get_tasks(self):
        # Update task statuses based on current date
        for task in self.tasks:
            task['status'] = self.determine_status(task)
        return self.tasks

    def determine_status(self, task):
        today = datetime.now().date()
        if task['completed']:
            return 'Completed'
        due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
        if due_date < today:
            return 'Overdue'
        elif due_date == today:
            return 'Due Today'
        elif due_date == today + timedelta(days=1):
            return 'Upcoming'
        else:
            return 'Pending'

    def get_task_color(self, task):
        status = task['status']
        if status == 'Overdue':
            return 'red'
        elif status == 'Due Today':
            return 'green'
        elif status == 'Upcoming':
            return 'yellow'
        else:
            return 'grey50'

    def complete_task(self, task_id, comment=''):
        self.db.mark_task_complete(task_id, comment)
        self.reload_tasks()

    def calculate_due_date(self, task):
        # Simplified due date calculation; extend as needed
        recurrence = task.get('recurrence', 'one-time')
        today = datetime.now().date()
        if recurrence == 'daily':
            return today.strftime("%Y-%m-%d")
        elif recurrence == 'weekly':
            next_week = today + timedelta(weeks=1)
            return next_week.strftime("%Y-%m-%d")
        elif recurrence == 'monthly':
            next_month = today.replace(day=28) + timedelta(days=4)
            return next_month.replace(day=1).strftime("%Y-%m-%d")
        else:
            return task.get('due_date', today.strftime("%Y-%m-%d"))
