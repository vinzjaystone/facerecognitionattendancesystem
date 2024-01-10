from datetime import datetime

def do_timein() -> dict:
    # _tz = pytz.timezone("Asia/Manila")
    _time = datetime.now()
    time_format = "%H:%M:%S %m-%d-%Y"
    f_time = datetime.strftime(_time, time_format)
    print(f_time)
    status = ""
    hour, date = f_time.split(" ")

    late_threshold = datetime.strptime("09:15:00", "%H:%M:%S").time()
    overtime_threshold = datetime.strptime("17:00:00", "%H:%M:%S").time()
    time_in = datetime.strptime(hour, "%H:%M:%S").time()

    # Check for late
    if time_in > late_threshold:
        status = "LATE"
    else:
        status = "IN-TIME"
    # Check for overtime
    if time_in > overtime_threshold:
        status = "OVER-TIME"
    return {"hour": hour, "date": date, "status": status}


print(do_timein())
