from datetime import datetime, timedelta

def calculate_extra_date(last_date, num_days=1):
    # Convert the last date to a datetime object
    last_date = datetime.strptime(last_date, "%Y-%m-%d")

    # Calculate the next date by adding num_days
    next_date = last_date + timedelta(days=num_days)

    # Convert the next date back to a string in the "YYYY-MM-DD" format
    return next_date.strftime("%Y-%m-%d")