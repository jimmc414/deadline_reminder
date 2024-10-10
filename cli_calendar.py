import calendar
import datetime

def create_calendar(year, month):
    # Get the calendar for the specified month
    cal = calendar.monthcalendar(year, month)
    
    # Get the month name and create the header
    month_name = calendar.month_name[month]
    header = f"{month_name} {year}".center(20)
    
    # Create the day names header
    days = "Mo Tu We Th Fr Sa Su"
    
    # Build the calendar string
    cal_str = f"\033[1m{header}\033[0m\n\033[1m{days}\033[0m\n"
    
    for week in cal:
        week_str = ""
        for day in week:
            if day == 0:
                week_str += "   "
            else:
                if day == datetime.date.today().day and month == datetime.date.today().month and year == datetime.date.today().year:
                    week_str += f"\033[7m{day:2d}\033[0m "
                else:
                    week_str += f"{day:2d} "
        cal_str += week_str.rstrip() + "\n"
    
    return cal_str

def main():
    today = datetime.date.today()
    year = today.year
    month = today.month
    
    print("\033[1;36m┌──────────────────┐\033[0m")
    print(f"\033[1;36m│\033[0m {create_calendar(year, month).strip()} \033[1;36m│\033[0m")
    print("\033[1;36m└──────────────────┘\033[0m")

if __name__ == "__main__":
    main()