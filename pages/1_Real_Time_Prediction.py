import importlib
import streamlit as st

# from Home import facedetection
import Home as face
from streamlit_webrtc import webrtc_streamer
import av
import time


###################################################
st.title("FACERECOGNITION TIME IN/OUT")
###################################################
st.markdown("<hr>", unsafe_allow_html=True)
###################################################
col1, col2, col3 = st.columns(3)
with col1:
    # st.button("HELLO WORLD1")
    st.subheader("SET IN/OUT")
    options = ["IN", "OUT"]
    selected_option = st.radio(" ", options)
    st.write("You selected:", selected_option)
with col2:
    # st.button("HELLO WORLD2")
    st.subheader("SET REMARKS")
    options2 = ["LATE", "INTIME"]
    selected_option2 = st.radio(" ", options2)
    st.write("You selected:", selected_option2)
with col3:
    st.subheader("SELECT A DATE:")
    selected_date = st.date_input(" ", key="custom_date_input")
    # Display the selected date
    st.write("Selected Date:", selected_date)
###################################################
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("TEST TIMEIN BUTTON")
timein = st.button(
    "TEST TIMEIN", "testbtn", on_click=lambda: print("CALL TIME FUNCTION")
)
st.markdown("<hr>", unsafe_allow_html=True)
###################################################

container = st.container()
with container:
    st.subheader("Real-Time Attendance System")
    # Retrive the data from Redis Database
    with st.spinner("Retriving Data from Redis DB ..."):
        redis_face_db = face.facedetection.retrive_data(name="academy:register")
        csv_face_db = face.facedetection.retrive_data2(name='')

        print('----------------------------')
        print(type(redis_face_db))
        print(redis_face_db)
        print('----------------------------')
        print(type(csv_face_db))
        print(csv_face_db)
        print('----------------------------')


        st.dataframe(redis_face_db)
        st.dataframe(csv_face_db)

    st.success("Data sucessfully retrived from Redis")

# time
waitTime = 5  # time in sec
setTime = time.time()
realtimepred = face.facedetection.RealTimePred()  # real time prediction class


def video_frame_callback(frame):
    global setTime
    img = frame.to_ndarray(format="bgr24")  # 3 dimension numpy array
    # operation that you can perform on the array
    pred_img = realtimepred.face_prediction(
        img, csv_face_db, "facial_features", ["Name", "Role"], thresh=0.5
    )
    timenow = time.time()
    difftime = timenow - setTime
    if difftime >= waitTime:
        realtimepred.saveLogs_redis(
            inorout=selected_option, remark=selected_option2, selecteddate=selected_date
        )
        setTime = time.time()  # reset time
    return av.VideoFrame.from_ndarray(pred_img, format="bgr24")


webrtc_streamer(key="realtimePrediction", video_frame_callback=video_frame_callback)
