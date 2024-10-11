import calendar

def display_calendar(year, month):
    # Create a TextCalendar object
    cal = calendar.TextCalendar(calendar.SUNDAY)
    
    # Generate the month's calendar as a string
    month_calendar = cal.formatmonth(year, month)
    
    # Print the calendar
    print(month_calendar)

# Example usage
year = 2024
month = 10
display_calendar(year, month)
