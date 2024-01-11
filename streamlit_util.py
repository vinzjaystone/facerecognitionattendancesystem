from datetime import datetime
import pandas as pd
import streamlit as st
from io import BytesIO


def add_or_update_data(redisObj, base_key, data):
    """
    Add or update data in a Redis hash using HSET.

    Args:
    - redis_conn: Redis connection object
    - base_key: Base key for the hash (without the unique identifier)
    - data: Dictionary containing field-value pairs to be added or updated

    Returns:
    - True if data was added or updated, False otherwise
    """
    # Generate a unique identifier using a timestamp
    # unique_id = int(time.time() * 1000)  # Multiply by 1000 to get milliseconds

    # Append the unique identifier to the base key
    # key = f"{base_key}"
    key = base_key
    # Use HSET to add or update fields in the hash
    # HSET returns 1 if the field was added, 0 if the field was updated
    result = redisObj.hmset(key, data)
    return True if result else False


def do_timein() -> dict:
    # _tz = pytz.timezone("Asia/Manila")
    _time = datetime.now()
    time_format = "%H:%M:%S %m-%d-%Y"
    f_time = datetime.strftime(_time, time_format)
    # print(f_time)
    status = ""
    remarks = ""  # AMIN or AMOUT
    hour, date = f_time.split(" ")

    IN_T = datetime.strptime("09:30:00", "%H:%M:%S").time()
    OUT_T = datetime.strptime("11:59:00", "%H:%M:%S").time()

    late_threshold = datetime.strptime("09:15:00", "%H:%M:%S").time()
    overtime_threshold = datetime.strptime("17:00:00", "%H:%M:%S").time()
    time_in = datetime.strptime(hour, "%H:%M:%S").time()

    if time_in < IN_T:
        remarks = "IN"
    elif time_in > OUT_T:
        remarks = "OUT"

    # Check for late
    if time_in > late_threshold:
        status = "LATE"
    else:
        status = "IN-TIME"
    # Check for overtime
    if time_in > overtime_threshold:
        status = "OVER-TIME"

    return {"hour": hour, "date": date, "status": status, "remarks": remarks}


def get_data(redisObj, keys, fields_to_include):
    data = []
    for key in keys:
        values = {}
        for field in fields_to_include:
            value = redisObj.hget(key, field)
            decoded_value = value.decode('utf-8') if value else None
            values[field] = decoded_value
        data.append({'key': key.decode('utf-8'), **values})
    return data


def retrievetime(redisObj):
    # Specify the pattern to match
    base_key = "DTR"
    pattern = f"{base_key}:*"
    # Get all keys matching the pattern
    matching_keys = redisObj.keys(pattern)
    # Specify the fields you want to include in the result
    fields_to_include = ['name', 'date', 'AM-IN', 'AM-OUT', 'state']
    # Get data for each key with specific fields
    data = get_data(redisObj, matching_keys, fields_to_include)

    df = pd.DataFrame(data)
    # Allow the user to download the DataFrame as CSV
    csv_as_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", BytesIO(csv_as_bytes),
                       file_name='data.csv', key='download_csv')

    return data
