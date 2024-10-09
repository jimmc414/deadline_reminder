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
                     comment TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS audit_trail
                    (id INTEGER PRIMARY KEY,
                     task_id INTEGER,
                     completion_date TEXT,
                     comment TEXT)''')
    
    for task in tasks['tasks']:
        cursor.execute("""
            INSERT INTO tasks (name, due_date, recurrence, status)
            VALUES (?, ?, ?, ?)
        """, (task['name'], task['due_date'], task.get('recurrence', 'one-time'), 'pending'))
    
    conn.commit()
    conn.close()

def get_task_status(due_date):
    today = datetime.now().date()
    due = datetime.strptime(due_date, "%Y-%m-%d").date()
    
    if due < today:
        return "overdue"
    elif due == today:
        return "due today"
    elif due == today + timedelta(days=1):
        return "upcoming"
    else:
        return "pending"

def display_tasks():
    table = Table(title="Task List", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("No.", justify="right", style="cyan", no_wrap=True)
    table.add_column("Task", style="magenta")
    table.add_column("Due Date", style="green")
    table.add_column("Status", style="yellow")

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, due_date, status FROM tasks WHERE status != 'completed'")
    tasks = cursor.fetchall()

    for task in tasks:
        id, name, due_date, _ = task
        status = get_task_status(due_date)
        if status == "overdue":
            status_display = f"[red]{status}[/red]"
        elif status == "due today":
            status_display = f"[green]{status}[/green]"
        elif status == "upcoming":
            status_display = f"[yellow]{status}[/yellow]"
        else:
            status_display = f"[grey]{status}[/grey]"
        table.add_row(str(id), name, due_date, status_display)

    console.print(table)
    conn.close()

def mark_task_complete(task_id, comment=None):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    completion_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        UPDATE tasks
        SET status = ?, completion_date = ?, comment = ?
        WHERE id = ?
    """, ('completed', completion_date, comment, task_id))
    
    cursor.execute("""
        INSERT INTO audit_trail (task_id, completion_date, comment)
        VALUES (?, ?, ?)
    """, (task_id, completion_date, comment))
    
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
                comment = typer.prompt("Enter a comment (optional)")
                mark_task_complete(task_id, comment)
            except ValueError:
                console.print("Invalid input. Please enter a valid task number.", style="red")

if __name__ == "__main__":
    load_tasks_from_yaml('tasks.yaml')
    app()
