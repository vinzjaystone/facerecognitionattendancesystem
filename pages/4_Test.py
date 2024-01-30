import streamlit as st
from Home import facedetection
from facedetection import *
import pandas as pd
import calendar
import Home as face


import importlib
# from Home import facedetection
import Home as face
from streamlit_webrtc import webrtc_streamer
import av
import time

# st.set_page_config(page_title='Reporting',layout='wide')
st.subheader("Test")


tab1, tab2 = st.tabs(['Open Camera', 'Tab 2'])




redis_face_db = face.facedetection.retrive_data2(name='academy:register')
realtimepred = face.facedetection.RealTimePred()  # real time prediction class

print(redis_face_db)

# Real Time Prediction
# streamlit webrtc
# callback functionD


def video_frame_callback2(frame):
    print("CALLED NOW")
    img = frame.to_ndarray(format="bgr24")  # 3 dimension numpy array
    # operation that you can perform on the array
    pred_img = realtimepred.face_prediction(img, redis_face_db,
                                            'facial_features', ['Name', 'Role'], thresh=0.5)
    
    realtimepred.saveLogs_redis(
            inorout='IN', remark='LATE', selecteddate='2024/01/29')
    
    print(f"CALLED FOR - {frame}")
    

    # timenow = time.time()
    # difftime = timenow - setTime
    # if difftime >= waitTime:
    #     realtimepred.saveLogs_redis(
    #         inorout='IN', remark='LATE', selecteddate='2024/01/29')
    #     setTime = time.time()  # reset time
    #     # print('Save Data to redis database')
    #     # show_message("SUCCESSFULLY LOGOUT")

    # return av.VideoFrame.from_ndarray(pred_img, format="bgr24")

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")

    pred_img = realtimepred.face_prediction(img, redis_face_db,
                                            'facial_features', ['Name', 'Role'], thresh=0.5)

    # flipped = img[::-1,:,:]

    # return av.VideoFrame.from_ndarray(img, format="bgr24")
    return av.VideoFrame.from_ndarray(pred_img, format="bgr24")

# webrtc_streamer(key="realtimePrediction", video_frame_callback=video_frame_callback)

with tab1:
    webrtc_streamer(key="realtimePrediction", video_frame_callback=video_frame_callback)
#         # picture = st.camera_input("Take a picture")
#         # print(f"{picture}")

#         # if picture is not None:
#         #     st.image(picture)
#         #     print('YOW')

#         #     video_frame_callback(picture)
#         # else:
#         #     st.warning("No picture captured.")

# with tab2:
#     st.write("TAB 2")