import typer
from rich.console import Console
from rich.table import Table
from rich import box
import sqlite3
import yaml
from datetime import datetime, timedelta

app = typer.Typer()
console = Console()

def load_tasks_from_yaml(yaml_file):
    with open(yaml_file, 'r') as file:
        tasks = yaml.safe_load(file)
    
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                    (id INTEGER PRIMARY KEY,
                     name TEXT,
                     due_date TEXT,
                     recurrence TEXT,
                     status TEXT,
                     completion_date TEXT,
                     notes TEXT)''')
    
    for task in tasks['tasks']:
        cursor.execute("""
            INSERT OR REPLACE INTO tasks (id, name, due_date, recurrence, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task['id'], task['name'], task['due_date'], task.get('recurrence', 'one-time'), 'pending', task.get('notes', '')))
    
    conn.commit()
    conn.close()

def get_task_status_and_color(due_date, completion_date):
    today = datetime.now().date()
    due = datetime.strptime(due_date, "%Y-%m-%d").date()
    
    if completion_date:
        return "completed", "dim"
    
    if due < today:
        days_overdue = (today - due).days
        return f"overdue ({days_overdue} days)", "red"
    elif due == today:
        return "due today", "green"
    elif due == today + timedelta(days=1):
        return "due tomorrow", "yellow"
    else:
        return "pending", "dim"

def display_tasks():
    table = Table(title="Task List", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("No.", justify="right", style="cyan", no_wrap=True)
    table.add_column("Task", style="magenta")
    table.add_column("Due Date", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Last Completed", style="blue")
    table.add_column("Notes", style="white")

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, due_date, status, completion_date, notes FROM tasks")
    tasks = cursor.fetchall()

    for task in tasks:
        id, name, due_date, status, completion_date, notes = task
        status, color = get_task_status_and_color(due_date, completion_date)
        table.add_row(
            str(id),
            name,
            due_date,
            status,
            completion_date or "",
            notes or "",
            style=color
        )

    console.print(table)
    conn.close()

def mark_task_complete(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    completion_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        UPDATE tasks
        SET status = ?, completion_date = ?
        WHERE id = ?
    """, ('completed', completion_date, task_id))
    
    conn.commit()
    conn.close()
    console.print(f"Task {task_id} marked as complete.", style="green")

@app.command()
def run():
    while True:
        display_tasks()
        action = typer.prompt("Enter task number to mark as complete, 'r' to refresh, or 'q' to quit")
        
        if action.lower() == 'q':
            break
        elif action.lower() == 'r':
            continue
        else:
            try:
                task_id = int(action)
                mark_task_complete(task_id)
            except ValueError:
                console.print("Invalid input. Please enter a valid task number.", style="red")

if __name__ == "__main__":
    load_tasks_from_yaml('tasks.yaml')
    app()