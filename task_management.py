import yaml
from data_persistence import Database
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

class TaskManager:
    def __init__(self):
        self.db = Database()
        self.tasks_config = self.load_tasks_config()
        self.tasks = self.load_tasks_from_db()

    def load_tasks_config(self):
        try:
            with open('tasks.yaml', 'r') as file:
                return yaml.safe_load(file)['tasks']
        except FileNotFoundError:
            return []  # Return an empty list if the file doesn't exist

    def load_tasks_from_db(self):
        tasks = self.db.get_all_tasks()
        if not tasks:
            # Initialize tasks in the database
            for task in self.tasks_config:
                due_date = self.calculate_due_date(task)
                notes = task.get('notes', '')
                self.db.add_task(task['id'], task['name'], due_date, notes)
            tasks = self.db.get_all_tasks()
        
        # Ensure all tasks have the required fields
        for task in tasks:
            if 'completed' not in task:
                task['completed'] = False
            if 'due_date' not in task or task['due_date'] is None:
                task['due_date'] = date.today().strftime("%Y-%m-%d")
            if 'start_date' not in task:
                task['start_date'] = task['due_date']
            if 'recurrence' not in task:
                task['recurrence'] = 'one-time'  # Default to one-time if not specified
            if 'notes' not in task:
                task['notes'] = ''
        
        return tasks

    def add_task(self, task_data):
        # Generate a new unique ID
        new_id = max([task['id'] for task in self.tasks], default=0) + 1
        task_data['id'] = new_id

        # Add the 'completed' key
        task_data['completed'] = False

        # Set the initial due date to the start date if not provided
        if 'due_date' not in task_data or task_data['due_date'] is None:
            task_data['due_date'] = task_data['start_date']

        # Ensure all required fields are present
        task_data['recurrence'] = task_data.get('recurrence', 'one-time')
        task_data['notes'] = task_data.get('notes', '')

        # Add the new task to the list
        self.tasks.append(task_data)

        # Update the YAML file
        self.save_tasks_to_yaml()

        # Add the task to the database
        self.db.add_task(new_id, task_data['name'], task_data['due_date'], task_data['notes'])

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

    def calculate_due_date(self, task):
        recurrence = task.get('recurrence', 'one-time')
        start_date = datetime.strptime(task.get('start_date', date.today().strftime("%Y-%m-%d")), "%Y-%m-%d").date()
        
        if recurrence == 'daily':
            return start_date.strftime("%Y-%m-%d")
        elif recurrence == 'weekly':
            return start_date.strftime("%Y-%m-%d")
        elif recurrence == 'monthly':
            return start_date.strftime("%Y-%m-%d")
        else:  # one-time or custom date
            return task.get('due_date', start_date.strftime("%Y-%m-%d"))

    def calculate_next_due_date(self, task):
        start_date = datetime.strptime(task['start_date'], "%Y-%m-%d").date()
        current_due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
        recurrence = task.get('recurrence', 'one-time')

        if recurrence == 'daily':
            return (current_due_date + timedelta(days=1)).strftime("%Y-%m-%d")
        elif recurrence == 'weekly':
            return (current_due_date + timedelta(weeks=1)).strftime("%Y-%m-%d")
        elif recurrence == 'monthly':
            next_due_date = current_due_date + relativedelta(months=1)
            # Adjust for months with fewer days
            while next_due_date.month == (current_due_date + relativedelta(months=1)).month:
                next_due_date -= timedelta(days=1)
            return next_due_date.strftime("%Y-%m-%d")
        else:  # one-time or unknown recurrence
            return task['due_date']

    def get_tasks(self):
        today = date.today()
        for task in self.tasks:
            task_due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
            if task_due_date < today and not task['completed']:
                if task.get('recurrence', 'one-time') != 'one-time':
                    # Calculate the next due date
                    task['due_date'] = self.calculate_next_due_date(task)
                    # Update the task in the database
                    self.db.update_task_due_date(task['id'], task['due_date'])
            task['status'] = self.determine_status(task)
        return self.tasks

    def determine_status(self, task):
        today = date.today()
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
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                break
        self.db.mark_task_complete(task_id, comment)

    def reload_tasks(self):
        self.tasks = self.load_tasks_from_db()

    def get_last_completed_date(self, task_id):
        return self.db.get_last_completed_date(task_id)