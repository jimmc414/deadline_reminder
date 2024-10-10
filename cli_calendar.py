import calendar
import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich import box
import argparse

# def create_info_section():
    # info_table = Table(show_header=False, box=box.SIMPLE, expand=True)
    # info_table.add_column("Key", style="cyan", no_wrap=True)
    # info_table.add_column("Value", style="magenta")
    
    # info_table.add_row("Current Time", datetime.datetime.now().strftime("%H:%M:%S"))
    # info_table.add_row("Week of Year", f"{datetime.date.today().isocalendar()[1]}")
    # info_table.add_row("Days Left in Year", f"{(datetime.date(datetime.date.today().year + 1, 1, 1) - datetime.date.today()).days}")
    
    # return Panel(info_table, title="Calendar Information", border_style="bright_blue", padding=(1, 1), expand=True)

def create_calendar(year, month):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    calendar_table = Table(show_header=True, header_style="bold cyan", box=box.SQUARE, expand=True)
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        calendar_table.add_column(day, justify="center", style="cyan", no_wrap=True, ratio=1)

    today = datetime.date.today()

    for week in cal:
        row = []
        for day in week:
            if day == 0:
                cell = Text(" ", style="dim")
            else:
                date = datetime.date(year, month, day)
                if date == today:
                    cell = Text(f"{day:2d}", style="bold white on blue")
                elif date.weekday() >= 5:  # Weekend
                    cell = Text(f"{day:2d}", style="italic yellow")
                else:
                    cell = Text(f"{day:2d}", style="white")
            
            row.append(Panel(cell, expand=True, border_style="bright_black"))
        
        calendar_table.add_row(*row)

    title = Text("❰ ", style="bold yellow") + Text(f"{month_name} {year}", style="bold magenta") + Text(" ❱", style="bold yellow")
    
    calendar_panel = Panel(
        calendar_table,
        title=title,
        subtitle=f"Week {today.isocalendar()[1]} of {today.year}",
        expand=True,
        border_style="none",  # Remove the border
        padding=(0, 1),
    )

    return calendar_panel

def main():
    parser = argparse.ArgumentParser(description="Display an enhanced CLI calendar using rich.")
    parser.add_argument("-y", "--year", type=int, help="Year to display (default: current year)")
    parser.add_argument("-m", "--month", type=int, help="Month to display (default: current month)")
    args = parser.parse_args()

    today = datetime.date.today()
    year = args.year or today.year
    month = args.month or today.month

    console = Console()
    
    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="info", size=5),
        Layout(name="calendar", ratio=1)
    )
    
    # Add content to layout
    # layout["info"].update(create_info_section())
    layout["calendar"].update(create_calendar(year, month))
    
    console.print(layout)

if __name__ == "__main__":
    main()