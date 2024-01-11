import streamlit as st 
from Home import facedetection
import pandas as pd
# st.set_page_config(page_title='Reporting',layout='wide')
st.subheader('Reporting')


# Retrive logs data and show in Report.py
# extract data from redis list
name = 'attendance:logs'
def load_logs(name,end=-1):
    logs_list = facedetection.redisObj.lrange(name,start=0,end=end) # extract all data from the redis database
    return logs_list

# tabs to show the info
tab1, tab2, tab3 = st.tabs(['Registered Data','Logs', 'Test TimeInOut'])

with tab1:
    if st.button('Refresh Data'):
        # Retrive the data from Redis Database
        with st.spinner('Retriving Data from Redis DB ...'):    
            redis_face_db = facedetection.retrive_data(name='academy:register')
            st.dataframe(redis_face_db[['Name','Role']])

with tab2:
    if st.button('Refresh Logs'):
        st.write(load_logs(name=name))
        
with tab3:
    if st.button("Refresh Time IN-OUT"):
        # # Create a Pandas DataFrame
        # localData = face_rec.retrieve_loginout_data()
        # df = pd.DataFrame(localData)

        # data = face_rec.retrievetime()
        # df = pd.DataFrame(data)

        with st.spinner('Retriving Data from Redis DB ...'):    
            redis_face_db = facedetection.getTimeInOut()
            st.dataframe(redis_face_db)

