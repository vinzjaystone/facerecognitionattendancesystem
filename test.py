# import logging
# import numpy as np
# import pandas as pd
# import cv2
# from io import BytesIO
import redis
# import random
# # insight face
# import streamlit as st
# from insightface.app import FaceAnalysis
# from sklearn.metrics import pairwise
# from extra.localdb import LocalDB
# # time
# from datetime import datetime
# import os
from streamlit_util import add_or_update_data, do_timein, retrievetime


# Connect to Redis Client
# hostname = "redis-11244.c323.us-east-1-2.ec2.cloud.redislabs.com"
user = 'vinz'
hostname = "172.104.35.79"
# portnumber = 11244
portnumber = 6379
# password = "cwwFaiD50FXDQa7Yc16beWEjANlkGFWJ"
password = "testpassword"

redisObj = redis.StrictRedis(host=hostname, port=portnumber, password=password, decode_responses=False)
# localDB = LocalDB("./database/timeinout.db")
hash_key = "academy:register"

values = redisObj.hgetall(hash_key)