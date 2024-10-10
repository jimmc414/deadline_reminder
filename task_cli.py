from rich.console import Console
from rich.table import Table
from task_management import TaskManager
from logging_and_undo import Logger
import time

console = Console()

def display_tasks(task_manager):
    table = Table(title="Task List")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Task Name", style="magenta")
    table.add_column("Due Date", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Last Completed", style="blue")  # New column for last completed date
    table.add_column("Notes", style="white")

    tasks = task_manager.get_tasks()

    for task in tasks:
        status_color = task_manager.get_task_color(task)
        last_completed_date = task_manager.get_last_completed_date(task['id']) or 'N/A'
        
        table.add_row(
            str(task['id']),
            task['name'],
            task['due_date'],
            f"[{status_color}]{task['status']}[/{status_color}]",
            last_completed_date,  # Display last completed date
            task.get('notes', '')
        )

    console.print(table)

def add_task_prompt(task_manager):
    console.print("Adding a new task:")
    name = console.input("Task name: ")
    recurrence = console.input("Recurrence (daily/weekly/monthly/one-time): ")
    
    # Prompt for start date
    while True:
        start_date_input = console.input("Start date (YYYY-MM-DD, press Enter for today): ")
        if start_date_input == "":
            start_date = date.today()
            break
        else:
            try:
                start_date = datetime.strptime(start_date_input, "%Y-%m-%d").date()
                break
            except ValueError:
                console.print("Invalid date format. Please use YYYY-MM-DD.")
    
    due_date = None
    if recurrence == 'one-time':
        while True:
            due_date_input = console.input("Due date (YYYY-MM-DD): ")
            try:
                due_date = datetime.strptime(due_date_input, "%Y-%m-%d").date()
                if due_date < start_date:
                    console.print("Due date cannot be earlier than start date. Please enter a valid date.")
                else:
                    break
            except ValueError:
                console.print("Invalid date format. Please use YYYY-MM-DD.")
    
    notes = console.input("Notes (optional): ")

    task_data = {
        'name': name,
        'recurrence': recurrence,
        'start_date': start_date.strftime("%Y-%m-%d"),
        'due_date': due_date.strftime("%Y-%m-%d") if due_date else None,
        'notes': notes
    }

    task_manager.add_task(task_data)
    console.print("Task added successfully!")
    
def delete_task_prompt(task_manager):
    task_id = console.input("Enter the ID of the task to delete: ")
    if task_id.isdigit():
        task_id = int(task_id)
        task_manager.delete_task(task_id)
        console.print(f"Task {task_id} deleted successfully!")
    else:
        console.print("Invalid task ID. Please enter a number.")

def main():
    task_manager = TaskManager()
    logger = Logger()

    while True:
        console.clear()
        display_tasks(task_manager)

        console.print("\nEnter the task ID to mark as complete, 'a' to add a task, 'd' to delete a task, 'u' to undo last action, 'e' to export logs, 'q' to quit.")
        user_input = console.input("Your choice: ")

        if user_input.lower() == 'q':
            break
        elif user_input.lower() == 'a':
            add_task_prompt(task_manager)
        elif user_input.lower() == 'd':
            delete_task_prompt(task_manager)
        elif user_input.lower() == 'u':
            if logger.undo_last_action():
                console.print("Last action undone.")
                task_manager.reload_tasks()
            else:
                console.print("No actions to undo.")
        elif user_input.lower() == 'e':
            logger.export_logs_to_csv()
            console.print("Logs exported to task_logs.csv.")
        elif user_input.isdigit():
            task_id = int(user_input)
            comment = console.input("Add a comment (optional): ")
            task_manager.complete_task(task_id, comment)
            logger.log_completion(task_id, comment)
            console.print(f"Task {task_id} marked as complete.")
        else:
            console.print("Invalid input. Please try again.")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
