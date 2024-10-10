# task_management.py

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
                notes = task.get('notes', '')
                self.db.add_task(task['id'], task['name'], due_date, notes)
            tasks = self.db.get_all_tasks()
        
        # Ensure all tasks have the 'completed' key
        for task in tasks:
            if 'completed' not in task:
                task['completed'] = False
        
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
        else:  # one-time or custom date
            return task.get('due_date', today.strftime("%Y-%m-%d"))

    def get_last_completed_date(self, task_id):
        return self.db.get_last_completed_date(task_id)

    def add_task(self, task_data):
        # Generate a new unique ID
        new_id = max([task['id'] for task in self.tasks], default=0) + 1
        task_data['id'] = new_id

        # Add the 'completed' key
        task_data['completed'] = False

        # Calculate the due date
        task_data['due_date'] = self.calculate_due_date(task_data)

        # Add the new task to the list
        self.tasks.append(task_data)

        # Update the YAML file
        self.save_tasks_to_yaml()

        # Add the task to the database
        notes = task_data.get('notes', '')
        self.db.add_task(new_id, task_data['name'], task_data['due_date'], notes)

    def delete_task(self, task_id):
        # Remove the task from the list
        self.tasks = [task for task in self.tasks if task['id'] != task_id]

        # Update the YAML file
        self.save_tasks_to_yaml()

        # Remove the task from the database
        self.db.delete_task(task_id)

    def save_tasks_to_yaml(self):
        with open('tasks.yaml', 'w') as file:
            yaml.dump({'tasks': self.tasks}, file)

    # Replace the existing load_tasks_config method with this updated version
    def load_tasks_config(self):
        try:
            with open('tasks.yaml', 'r') as file:
                return yaml.safe_load(file)['tasks']
        except FileNotFoundError:
            return []  # Return an empty list if the file doesn't exist