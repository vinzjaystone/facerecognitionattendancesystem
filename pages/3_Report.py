import streamlit as st
from Home import facedetection
from facedetection import *
import pandas as pd
import calendar

# st.set_page_config(page_title='Reporting',layout='wide')
st.subheader("Reporting")


##################################################
# ATTENDANCE TRACKING  #
def days_per_week(year, month):
    # Get the calendar for the given month and year
    cal = calendar.monthcalendar(year, month)

    # Initialize a list to store the days per week
    days_by_week = []

    # Iterate over the weeks in the month
    for week in cal:
        # Filter out days that belong to the previous or next month
        days_in_week = [day for day in week if day != 0]
        days_by_week.append(days_in_week)

    return days_by_week


##################################################


# Retrive logs data and show in Report.py
# extract data from redis list
name = "attendance:logs"


def load_logs(name, end=-1):
    logs_list = facedetection.redisObj.lrange(
        name, start=0, end=end
    )  # extract all data from the redis database
    return logs_list


# tabs to show the info
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Registered Data", "Logs", "Test TimeInOut", "Attendance Tracking", "Extra"]
)

with tab1:
    if st.button("Refresh Data"):
        # Retrive the data from Redis Database
        with st.spinner("Retriving Data from Redis DB ..."):
            redis_face_db = facedetection.retrive_data(name="academy:register")
            st.dataframe(redis_face_db[["Name", "Role"]])

with tab2:
    if st.button("Refresh Logs"):
        st.write(load_logs(name=name))

with tab3:
    if st.button("Refresh Time IN-OUT"):
        # # Create a Pandas DataFrame
        # localData = face_rec.retrieve_loginout_data()
        # df = pd.DataFrame(localData)

        # data = face_rec.retrievetime()
        # df = pd.DataFrame(data)

        with st.spinner("Retriving Data from Redis DB ..."):
            redis_face_db = facedetection.getTimeInOut()
            print(redis_face_db)
            st.dataframe(redis_face_db)

with tab4:

    def change():
        print(f"WIDGET CHANGE : {users}")

    st.subheader("Attendance Tracking")
    # data = []
    # data.append({'name': 'vinz', 'age': 31})
    # data.append({'name': 'clarissa', 'age': 26})
    names = tuple(["vinz", "Unknown"])
    users = st.selectbox(label="Select Person", options=names, on_change=change)
    localData = retrieve_local_data2(users)
    if localData:
        df = pd.DataFrame(localData)
        # st.dataframe(df)
        st.markdown("<hr>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader("JANUARY")
            st.write("Present : 9")
            st.write("Absent : 1")
        with col2:
            st.subheader("FEBRUARY")
            st.write("Present : 9")
            st.write("Absent : 1")
        with col3:
            st.subheader("MARCH")
            st.write("Present : 9")
            st.write("Absent : 1")
        with col4:
            st.subheader("APRIL")
            st.write("Present : 9")
            st.write("Absent : 1")

        st.markdown("<hr>", unsafe_allow_html=True)
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.subheader("MAY")
            st.write("Present : 9")
            st.write("Absent : 1")
        with col6:
            st.subheader("JUNE")
            st.write("Present : 9")
            st.write("Absent : 1")
        with col7:
            st.subheader("JULY")
            st.write("Present : 9")
            st.write("Absent : 1")
        with col8:
            st.subheader("AUGUST")
            st.write("Present : 9")
            st.write("Absent : 1")

        st.markdown("<hr>", unsafe_allow_html=True)
        col9, col10, col11, col12 = st.columns(4)
        with col9:
            st.subheader("SEPTEMBER")
            st.write("Present : 9")
            st.write("Absent : 1")
        with col10:
            st.subheader("OCTOBER")
            st.write("Present : 9")
            st.write("Absent : 1")
        with col11:
            st.subheader("NOVEMBER")
            st.write("Present : 9")
            st.write("Absent : 1")
        with col12:
            st.subheader("DECEMBER")
            st.write("Present : 9")
            st.write("Absent : 1")
    # localData = retrieve_local_data2()

    # df = pd.DataFrame(localData)

    # st.dataframe(df)

import pandas as pd
import random

with tab5:
    st.subheader("EXTRA TABLE")

    df = pd.DataFrame(
        {
            "name": ["Roadmap", "Extras", "Issues"],
            "url": [
                "https://roadmap.streamlit.app",
                "https://extras.streamlit.app",
                "https://issues.streamlit.app",
            ],
            "stars": [random.randint(0, 1000) for _ in range(3)],
            "views_history": [
                [random.randint(0, 5000) for _ in range(30)] for _ in range(3)
            ],
        }
    )

    st.dataframe(
        df,
        column_config={
            "name": "App name",
            "stars": st.column_config.NumberColumn(
                "Github Stars",
                help="Number of stars on GitHub",
                format="%d ⭐",
            ),
            "url": st.column_config.LinkColumn("App URL"),
            "views_history": st.column_config.LineChartColumn(
                "Views (past 30 days)", y_min=0, y_max=5000
            ),
        },
        hide_index=True,
    )

    data = {
        "date": ["1", "2"],
        "month": ["1", "1"],
        "name": ["v", "v"],
        "role": ["s", "s"],
        "total-present": [1, 1],
        "total-absent": [0, 0],
    }

    st.dataframe(data)


# >>> import random
# >>> import pandas as pd
# >>> import streamlit as st
# >>>
# >>> df = pd.DataFrame(
# >>>     {
# >>>         "name": ["Roadmap", "Extras", "Issues"],
# >>>         "url": ["https://roadmap.streamlit.app", "https://extras.streamlit.app", "https://issues.streamlit.app"],
# >>>         "stars": [random.randint(0, 1000) for _ in range(3)],
# >>>         "views_history": [[random.randint(0, 5000) for _ in range(30)] for _ in range(3)],
# >>>     }
# >>> )
# >>> st.dataframe(
# >>>     df,
# >>>     column_config={
# >>>         "name": "App name",
# >>>         "stars": st.column_config.NumberColumn(
# >>>             "Github Stars",
# >>>             help="Number of stars on GitHub",
# >>>             format="%d ⭐",
# >>>         ),
# >>>         "url": st.column_config.LinkColumn("App URL"),
# >>>         "views_history": st.column_config.LineChartColumn(
# >>>             "Views (past 30 days)", y_min=0, y_max=5000
# >>>         ),
# >>>     },
# >>>     hide_index=True,
# >>> )
