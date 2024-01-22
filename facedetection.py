import logging
import numpy as np
import pandas as pd
import cv2
from io import BytesIO
import redis
import random
# insight face
import streamlit as st
from insightface.app import FaceAnalysis
from sklearn.metrics import pairwise
from extra.localdb import LocalDB
# time
from datetime import datetime
import os
from streamlit_util import add_or_update_data, do_timein, retrievetime


# Connect to Redis Client
hostname = "redis-11244.c323.us-east-1-2.ec2.cloud.redislabs.com"
portnumber = 11244
password = "cwwFaiD50FXDQa7Yc16beWEjANlkGFWJ"

redisObj = redis.StrictRedis(host=hostname, port=portnumber, password=password)

localDB = LocalDB("./database/timeinout.db")


# Retrive Data from database
def retrive_data(name):
    retrive_dict = redisObj.hgetall(name)
    retrive_series = pd.Series(retrive_dict)
    retrive_series = retrive_series.apply(
        lambda x: np.frombuffer(x, dtype=np.float32))
    index = retrive_series.index
    index = list(map(lambda x: x.decode(), index))
    retrive_series.index = index
    retrive_df = retrive_series.to_frame().reset_index()
    retrive_df.columns = ["name_role", "facial_features"]
    retrive_df[["Name", "Role"]] = (
        retrive_df["name_role"].apply(lambda x: x.split("@")).apply(pd.Series)
    )
    return retrive_df[["Name", "Role", "facial_features"]]


def retrieve_local_data():
    data = localDB.retrieve_time_data()
    df = pd.DataFrame(
        data,
        columns=["id", "name", "role", "tIn", "tOut", "date", "day", "month", "year", "remark"],
    )
    result_data = {col: pd.Series(df[col]).tolist() for col in df.columns}
    return result_data

def retrieve_local_data2(name):
    data = localDB.retrieve_time_data2(name)
    df = pd.DataFrame(
        data,
        columns=["id", "name", "role", "tIn", "tOut", "date", "day", "month", "year", "remark"],
    )
    result_data = {col: pd.Series(df[col]).tolist() for col in df.columns}
    return result_data


# configure face analysis
faceapp = FaceAnalysis(
    name="buffalo_sc", root="insightface_model", providers=["CPUExecutionProvider"]
)
faceapp.prepare(ctx_id=0, det_size=(640, 640), det_thresh=0.5)


# ML Search Algorithm
def ml_search_algorithm(
    dataframe, feature_column, test_vector, name_role=["Name", "Role"], thresh=0.5
):
    """
    cosine similarity base search algorithm
    """
    # step-1: take the dataframe (collection of data)
    dataframe = dataframe.copy()
    # step-2: Index face embeding from the dataframe and convert into array
    X_list = dataframe[feature_column].tolist()
    x = np.asarray(X_list)

    # step-3: Cal. cosine similarity
    similar = pairwise.cosine_similarity(x, test_vector.reshape(1, -1))
    similar_arr = np.array(similar).flatten()
    dataframe["cosine"] = similar_arr

    # step-4: filter the data
    data_filter = dataframe.query(f"cosine >= {thresh}")
    if len(data_filter) > 0:
        # step-5: get the person name
        data_filter.reset_index(drop=True, inplace=True)
        argmax = data_filter["cosine"].argmax()
        person_name, person_role = data_filter.loc[argmax][name_role]

    else:
        person_name = "Unknown"
        person_role = "Unknown"

    return person_name, person_role


def getTimeInOut():
    return retrievetime(redisObj)

# Real Time Prediction
# we need to save logs for every 1 mins


class RealTimePred:
    def __init__(self):
        self.logs = dict(name=[], role=[], current_time=[])

    def reset_dict(self):
        self.logs = dict(name=[], role=[], current_time=[])
    
    def save_to_localdb(self, data, inorout, role):
        # Add to local database too
        # init database object
        DB_NAME = './database/timeinout.db'
        db = LocalDB(DB_NAME)
        # prepare db keys
        month, day, year = data['date'].split('-')
        db_name = data['name']
        db_role = role
        remark = data['state']
        # Set as Blank or N/A
        date = data['date']
        col_prefix = ""

        # CHECK FOR EXISTING ENTRY
        query = f"SELECT COUNT(*) FROM timeinTBL WHERE name='{db_name}' and date='{date}' "
        res = db.executeQuery(query, dbName=DB_NAME, ret=True)
        count = res[0]['COUNT(*)'] 


        if count < 1:
            tIn = data['AM-IN']
            tOut = 'N/A' 
            # check if timin is IN or OUT?
            col_prefix = 'tIn'
            # if in its a new entry so INSERT
            query = f"""
                INSERT into timeinTBL (name, role, tIn, tOut, date, day, month, year, remark)
                VALUES('{db_name}', '{db_role}', '{tIn}', '{tOut}', '{date}', '{day}', '{month}', '{year}', '{remark}')
            """
            db.executeQuery(query, dbName=DB_NAME)
        else:
            if inorout == 'IN':
                col_prefix = 'tIn'
                tIn = data['AM-IN']
                query = f"""
                UPDATE timeinTBL
                SET {col_prefix} = '{tIn}'
                WHERE name='{db_name}' and date='{date}'
                """
            else:
                col_prefix = 'tOut'
                tOut = data['AM-OUT']
                query = f"""
                UPDATE timeinTBL
                SET {col_prefix} = '{tOut}'
                WHERE name='{db_name}' and date='{date}'
                """
            db.executeQuery(query, dbName=DB_NAME)

        print(f"DATA FOR DATABASE : {data} SAVED...")

    def saveLogs_redis(self, inorout=None, remark=None, selecteddate=None):
        # step-0: get time of face detection along with DTR Logic and State
        d_time = do_timein()
        # step-1: create a logs dataframe
        dataframe = pd.DataFrame(self.logs)
        # step-2: drop the duplicate information (distinct name)
        dataframe.drop_duplicates("name", inplace=True)
        # step-3: push data to redis database (list)
        # encode the data
        name_list = dataframe["name"].tolist()
        role_list = dataframe["role"].tolist()
        ctime_list = dataframe["current_time"].tolist()
        encoded_data = []
        for name, role, ctime in zip(name_list, role_list, ctime_list):
            if name != "Unknown":
                concat_string = f"{name}@{role}@{ctime}"
                encoded_data.append(concat_string)


                hour = d_time['hour']
                # date = d_time['date']
                date = ""
                if selecteddate != None:
                    final_format = "%m-%d-%Y"
                    formatted_date_str = selecteddate.strftime(final_format)
                    # Format date to accepted by database
                    date = formatted_date_str
                state = ""
                if remark != None:
                    state = remark
                
                # state = d_time['status']
                # remarks = ""
                # if remark != None:
                #     remarks = remark
                # else:
                #     remarks = d_time['remarks']

                base_key = f"DTR:{date}:{name}"
                data = {}

                # For testing purposes
                # if 1 set as IN if 2 set as OUT
                # ran = random.randint(1, 2)

                if inorout == 'IN':
                    # if ran == 1:
                    data = {"date": date, "name": name,
                            "AM-IN": hour, 'state': state}
                else:
                    data = {"date": date, "name": name,
                            "AM-OUT": hour, 'state': state}
                    
                # logging.debug(f"DATA : {data} |  INFO : {d_time}")

                # Add or update data in the hash with a unique identifier
                # this function also decides whether to insert a new hash or update an existing hash
                added_or_updated = add_or_update_data(redisObj, base_key, data)

                self.save_to_localdb(data, inorout, role)
                
                


                if added_or_updated:
                    logging.debug(
                        f"Data added or updated with unique identifier in {base_key}")
                else:
                    logging.debug(f"Failed to add or update data in {base_key}")
            else:
                # Test data
                concat_string = f"Unkown@{role}{ctime}"
                encoded_data.append(concat_string)

                hour = d_time['hour']
                # date = d_time['date']
                date = ""
                if selecteddate != None:
                    final_format = "%m-%d-%Y"
                    formatted_date_str = selecteddate.strftime(final_format)
                    # Format date to accepted by database
                    date = formatted_date_str
                state = ""
                if remark != None:
                    state = remark

                base_key = f"DTR:{date}:{name}"
                data = {}

                # For testing purposes
                # if 1 set as IN if 2 set as OUT
                # ran = random.randint(1, 2)

                if inorout == 'IN':
                    # if ran == 1:
                    data = {"date": date, "name": name,
                            "AM-IN": hour, 'state': state}
                else:
                    data = {"date": date, "name": name,
                            "AM-OUT": hour, 'state': state}
                    
                print(f'DATA FOR DB : {base_key}  -  {data}')


                self.save_to_localdb(data, inorout, 'DEV')
                
        # if len(encoded_data) > 0:
        #     redisObj.lpush("attendance:logs", *encoded_data)

        self.reset_dict()
        print("LOGIN SUCCESSFUL")
        # st.success("SUCCESSFUL LOGIN")

    # TODO:
    def save_timein(self):
        d_time = do_timein()
        # step-1: create a logs dataframe
        dataframe = pd.DataFrame(self.logs)
        # step-2: drop the duplicate information (distinct name)
        dataframe.drop_duplicates("name", inplace=True)
        # step-3: push data to redis database (list)
        # encode the data
        name_list = dataframe["name"].tolist()
        role_list = dataframe["role"].tolist()
        ctime_list = dataframe["current_time"].tolist()
        encoded_data = []
        for name, role, ctime in zip(name_list, role_list, ctime_list):
            if name != "Unknown":
                concat_string = f"{name}@{role}@{ctime}"
                encoded_data.append(concat_string)

                # Get name

        # if len(encoded_data) > 0:
        #     redisObj.lpush("attendance:logs", *encoded_data)

        self.reset_dict()

    def face_prediction(
        self,
        test_image,
        dataframe,
        feature_column,
        name_role=["Name", "Role"],
        thresh=0.5,
    ):
        # step-1: find the time
        current_time = str(datetime.now())

        # step-1: take the test image and apply to insight face
        results = faceapp.get(test_image)
        test_copy = test_image.copy()
        # step-2: use for loop and extract each embedding and pass to ml_search_algorithm

        for res in results:
            x1, y1, x2, y2 = res["bbox"].astype(int)
            embeddings = res["embedding"]
            person_name, person_role = ml_search_algorithm(
                dataframe,
                feature_column,
                test_vector=embeddings,
                name_role=name_role,
                thresh=thresh,
            )
            if person_name == "Unknown":
                color = (0, 0, 255)  # bgr
            else:
                color = (0, 255, 0)

            cv2.rectangle(test_copy, (x1, y1), (x2, y2), color)

            text_gen = person_name
            cv2.putText(
                test_copy, text_gen, (x1,
                                      y1), cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2
            )
            cv2.putText(
                test_copy,
                current_time,
                (x1, y2 + 10),
                cv2.FONT_HERSHEY_DUPLEX,
                0.7,
                color,
                2,
            )
            # save info in logs dict
            self.logs["name"].append(person_name)
            self.logs["role"].append(person_role)
            self.logs["current_time"].append(current_time)

        return test_copy


# Registration Form
class RegistrationForm:
    def __init__(self):
        self.sample = 0

    def reset(self):
        self.sample = 0

    def get_embedding(self, frame):
        # get results from insightface model
        results = faceapp.get(frame, max_num=1)
        embeddings = None
        for res in results:
            self.sample += 1
            x1, y1, x2, y2 = res["bbox"].astype(int)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
            # put text samples info
            text = f"samples = {self.sample}"
            cv2.putText(
                frame, text, (x1,
                              y1), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 0), 2
            )

            # facial features
            embeddings = res["embedding"]

        return frame, embeddings

    def save_data_in_redis_db(self, name, role):
        # validation name
        if name is not None:
            if name.strip() != "":
                key = f"{name}@{role}"
            else:
                return "name_false"
        else:
            return "name_false"

        # if face_embedding.txt exists
        if "face_embedding.txt" not in os.listdir():
            return "file_false"

        # step-1: load "face_embedding.txt"
        x_array = np.loadtxt("face_embedding.txt",
                             dtype=np.float32)  # flatten array

        # step-2: convert into array (proper shape)
        received_samples = int(x_array.size / 512)
        x_array = x_array.reshape(received_samples, 512)
        x_array = np.asarray(x_array)

        # step-3: cal. mean embeddings
        x_mean = x_array.mean(axis=0)
        x_mean = x_mean.astype(np.float32)
        x_mean_bytes = x_mean.tobytes()

        # step-4: save this into redis database
        # redis hashes
        redisObj.hset(name="academy:register", key=key, value=x_mean_bytes)

        #
        os.remove("face_embedding.txt")
        self.reset()

        return True
