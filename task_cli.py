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
    table.add_column("Notes", style="white")

    tasks = task_manager.get_tasks()

    for task in tasks:
        status_color = task_manager.get_task_color(task)
        # Remove the strftime call since the due_date is already a string
        table.add_row(
            str(task['id']),
            task['name'],
            task['due_date'],  # It's already a string, no need for strftime
            f"[{status_color}]{task['status']}[/{status_color}]",
            task.get('notes', '')
        )

    console.print(table)

def main():
    task_manager = TaskManager()
    logger = Logger()

    while True:
        console.clear()
        display_tasks(task_manager)

        console.print("\nEnter the task ID to mark as complete, 'u' to undo last action, 'e' to export logs, 'q' to quit.")
        user_input = console.input("Your choice: ")

        if user_input.lower() == 'q':
            break
        elif user_input.lower() == 'u':
            if logger.undo_last_action():
                console.print("Last action undone.")
                task_manager.reload_tasks()
            else:
                console.print("No actions to undo.")
            time.sleep(1)
        elif user_input.lower() == 'e':
            logger.export_logs_to_csv()
            console.print("Logs exported to task_logs.csv.")
            time.sleep(1)
        elif user_input.isdigit():
            task_id = int(user_input)
            comment = console.input("Add a comment (optional): ")
            task_manager.complete_task(task_id, comment)
            logger.log_completion(task_id, comment)
            console.print(f"Task {task_id} marked as complete.")
            time.sleep(1)
        else:
            console.print("Invalid input. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()
