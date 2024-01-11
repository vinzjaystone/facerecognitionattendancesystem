import streamlit as st
from Home import facedetection
from streamlit_webrtc import webrtc_streamer
import av
import time

st.header("DEMO PURPOSES")
##
st.subheader("SET IF TIME IN/OUT")
options = ['IN', 'OUT']
selected_option = st.radio('STATE:', options)
st.write('You selected:', selected_option)
##
st.subheader("SET IF TIME IN/OUT")
options2 = ['LATE', 'INTIME']
selected_option2 = st.radio('REMARKS:', options2)
st.write('You selected:', selected_option2)
##
# Date input widget with custom styling
selected_date = st.date_input('Select a date:', key='custom_date_input')

# Display the selected date
st.write('Selected Date:', selected_date)


def show_message_box(message, message_type='info'):
    if message_type == 'success':
        st.success(message)
    elif message_type == 'info':
        st.info(message)
    elif message_type == 'warning':
        st.warning(message)
    elif message_type == 'error':
        st.error(message)

# if st.button("Click me to show MessageBox"):
#     # Show a success message box
#     # show_message_box(f"This is a success message!", message_type='info')

#     final_format = "%m-%d-%Y"
#     formatted_date_str = selected_date.strftime(final_format)
#     st.success(f"DATE : {formatted_date_str}")

    # show_message_box(f"IN/OUT : {selected_option}  STATE : {selected_option2}  DATE : {selected_date}", message_type='success')


async def show_message(message):
    # Your asynchronous code here
    st.success(message)


# st.set_page_config(page_title='Predictions')
st.subheader('Real-Time Attendance System')
# Retrive the data from Redis Database
with st.spinner('Retriving Data from Redis DB ...'):
    redis_face_db = facedetection.retrive_data(name='academy:register')
    st.dataframe(redis_face_db)

st.success("Data sucessfully retrived from Redis")

# time
waitTime = 5  # time in sec
setTime = time.time()
realtimepred = facedetection.RealTimePred()  # real time prediction class

# Real Time Prediction
# streamlit webrtc
# callback functionD


def video_frame_callback(frame):
    global setTime

    img = frame.to_ndarray(format="bgr24")  # 3 dimension numpy array
    # operation that you can perform on the array
    pred_img = realtimepred.face_prediction(img, redis_face_db,
                                            'facial_features', ['Name', 'Role'], thresh=0.5)

    timenow = time.time()
    difftime = timenow - setTime
    if difftime >= waitTime:
        realtimepred.saveLogs_redis(
            inorout=selected_option, remark=selected_option2, selecteddate=selected_date)
        setTime = time.time()  # reset time
        # print('Save Data to redis database')
        # show_message("SUCCESSFULLY LOGOUT")

    return av.VideoFrame.from_ndarray(pred_img, format="bgr24")


webrtc_streamer(key="realtimePrediction", video_frame_callback=video_frame_callback,
                rtc_configuration={
                    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                }
                )
