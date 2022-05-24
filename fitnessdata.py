import os
import json
import httplib2
import requests

import time
from datetime import datetime, timedelta
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from oauth2client.file import Storage

class calorie_record:
    def __init__(self, s, e, v, r):
        self.start = s
        self.end = e
        self.value = v
        self.reason = r

class step_record:
    def __init__(self, s, e, v):
        self.start = s
        self.end = e
        self.value = v

class sleep_record:
    def __init__(self, s, e, r):
        self.start = s
        self.end = e
        self.reason = r

class fitnessdata:
    def __init__(self, user_name):
        self.authdata = self.auth_data(user_name)
        return

    def get_transaction_cal(self, start_date, end_date):
        ret = []
        START = int(time.mktime(start_date.timetuple())*1000000000)
        # カロリーデータ集計を取得
        self.cal_data_raw = self.retrieve_data(start_date, end_date, "cal")
        if self.cal_data_raw["bucket"][0]["dataset"][0]["point"]==[]:
            return ret   # データ無いね
        for dataset in self.cal_data_raw["bucket"]:
            point = dataset["dataset"][0]["point"][0]
            if int(point["startTimeNanos"]) >= START:
                ret.append(
                    calorie_record(
                        int(point["startTimeNanos"]) / 1000000000 ,
                        int(point["endTimeNanos"]) / 1000000000,
                        point['value'][0]['fpVal'],
                        ""
                        )
                )
        # クラスメンバとして保持しておく
        self.cal_data = ret

    def get_transaction_sleep(self, start_date, end_date):
        ret = []
        START = int(time.mktime(start_date.timetuple())*1000000000)
        self.sleep_data_raw = self.retrieve_data(start_date, end_date, "sleep_post")
        # 睡眠データ集計を取得
        if self.sleep_data_raw["bucket"]==[]:
            return ret   # データ無いね
        for point in self.sleep_data_raw["bucket"][0]["dataset"][0]["point"]:
            if int(point["startTimeNanos"]) >= START:
                if point['value'][0]['intVal'] == 1:
                    # 目覚めている
                    reason = ""
                elif point['value'][0]['intVal'] == 2:
                    # 睡眠中
                    reason = "sleep"
                elif point['value'][0]['intVal'] == 3:
                    # ベッドの外にいる
                    reason = ""
                elif point['value'][0]['intVal'] == 4:
                    # 浅い眠り
                    reason = "light_sleep"
                elif point['value'][0]['intVal'] == 5:
                    # 深い眠り
                    reason = "deep_sleep"
                elif point['value'][0]['intVal'] == 6:
                    # レム睡眠
                    reason = "rem_sleep"
                else:
                    reason = ""
                if reason != "":
                    ret.append(
                        sleep_record(
                            int(int(point["startTimeNanos"]) / 1000000000) ,
                            int(int(point["endTimeNanos"]) / 1000000000),
                            reason,
                            )
                    )
        # クラスメンバとして保持しておく
        self.sleep_data = ret

    def get_transaction_sleep_session(self, start_date, end_date):
        ret = []
        self.sleep_session_data_raw = self.retrieve_data(start_date, end_date, "sleep_session")
        # 睡眠データ集計を取得
        if self.sleep_session_data_raw["session"]==[]:
            return ret   # データ無いね
        for point in self.sleep_session_data_raw["session"]:
            if int(point["activityType"]) == 72 :
                start_time = int(int(point["startTimeMillis"]) / 1000)
                end_time = int(int(point["endTimeMillis"]) / 1000)
                if  point["name"].startswith('Deep'):
                    reason = "Deep"
                elif  point["name"].startswith('Light'):        
                    reason = "Light"
                else:
                    reason = "sleep"
                ret.append(
                    sleep_record(start_time, end_time, reason)
                )
        # クラスメンバとして保持しておく
        self.sleep_session_data = ret

    def get_transaction_steps(self, start_date, end_date):
        ret = []
        START = int(time.mktime(start_date.timetuple())*1000000000)
        self.steps_data_raw = self.retrieve_data(start_date, end_date, "steps")
        # 睡眠データ集計を取得
        if self.steps_data_raw["bucket"][0]["dataset"][0]["point"]==[]:
            return ret   # データ無いね
        for dataset in self.steps_data_raw["bucket"]:
            point = dataset["dataset"][0]["point"][0]
            if int(point["startTimeNanos"]) >= START:
                ret.append(
                    step_record(
                        int(int(point["startTimeNanos"]) / 1000000000) ,
                        int(int(point["endTimeNanos"]) / 1000000000),
                        point['value'][0]['intVal'],
                        )
                )
        # クラスメンバとして保持しておく
        self.steps_data = ret

    def get_transaction(self, start_date, end_date):
        print("start_date:" + str(start_date) + "    end_date:" + str(end_date))
        self.get_transaction_cal(start_date, end_date)
        self.get_transaction_sleep(start_date, end_date)
        #self.get_transaction_sleep_session(start_date, end_date)
        self.get_transaction_steps(start_date, end_date)        

    OAUTH_SCOPE = [
        'https://www.googleapis.com/auth/fitness.activity.read',
        'https://www.googleapis.com/auth/fitness.sleep.read',
        'https://www.googleapis.com/auth/fitness.sleep.write'        
    ]
    DATA_SOURCE_STEP_COUNT = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
    DATA_SOURCE = {
        "steps": "derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas",
        "dist": "derived:com.google.distance.delta:com.google.android.gms:from_steps<-merge_step_deltas",
        "bpm": "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm",
        "rhr": "derived:com.google.heart_rate.bpm:com.google.android.gms:resting_heart_rate<-merge_heart_rate_bpm",
        "sleep" : "derived:com.google.sleep.segment:com.google.android.gms:sleep_from_activity<-raw:com.google.activity.segment:com.heytap.wearable.health:stream_sleep",
        "cal" : "derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended",
        "move": "derived:com.google.active_minutes:com.google.android.gms:from_steps<-estimated_steps",
        "points" : "derived:com.google.heart_minutes:com.google.android.gms:merge_heart_minutes",
        "weight" : "derived:com.google.weight:com.google.android.gms:merge_weight"
    }
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
    CREDENTIALS_FILE = "./credentials"

    def auth_data(self, user_name):
        credentials = ""
        self.file_name = self.CREDENTIALS_FILE + user_name
        if os.path.exists(self.file_name):
            credentials = Storage(self.file_name).get()
        else:
            flow = flow_from_clientsecrets(
                # API有効化時に取得したOAuth用のJSONファイルを指定
                './google-credentials.json',
                # スコープを指定
                scope=self.OAUTH_SCOPE,
                # ユーザーの認証後の、トークン受け取り方法を指定（後述）
                redirect_uri=self.REDIRECT_URI)

            authorize_url = flow.step1_get_authorize_url()
            print('下記URLをブラウザで起動してください。')
            print(authorize_url)

            code = input('Codeを入力してください: ').strip()
            credentials = flow.step2_exchange(code)

            if not os.path.exists(self.file_name):
                Storage(self.file_name).put(credentials)

        # Create an httplib2.Http object and authorize it with our credentials
        http = httplib2.Http()
        http = credentials.authorize(http)

        fitness_service = build('fitness', 'v1', http=http)
        self.authdata = fitness_service
        return fitness_service


    def retrieve_data(self, start_date, end_date, index):
        START = int(time.mktime(start_date.timetuple())*1000000000)
        NEXT = int(time.mktime(end_date.timetuple())*1000000000)
        data_set = "%s-%s" % (START, NEXT)
        if index=="cal":
            body =  {
                "aggregateBy": [{
                    "dataSourceId":
                    "derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended"
                }],
                "bucketByTime": { "durationMillis": "86400000" },
                "startTimeMillis": str(int(time.mktime(start_date.timetuple())) * 1000),
                "endTimeMillis": str(int(time.mktime(end_date.timetuple())) * 1000)
                }
            ret = self.authdata.users().dataset().aggregate(userId='me', body=body).execute()
        elif index=="sleep":
            # google API のリファレンスドキュメントだとどこに書いてあるのかよくわからんのだけど、下記の stackoverflow のトピックに書いてあったやりかた
            # https://stackoverflow.com/questions/64820336/huawei-watch-2-sleep-sessions-are-not-in-google-fit-api-sleep-endpoint
            # まじうんこ
            ret = self.authdata.users().dataSources().datasets().get(userId='me', dataSourceId=self.DATA_SOURCE[index], datasetId=data_set).execute()
        elif index=="sleep_post":
            # https://developers.google.com/fit/scenarios/read-sleep-data
            # 2.To obtain details of sleep stages for each session (if present), use the following request for each session in the filtered list:
            # に従う動きを 
            # https://googleapis.github.io/google-api-python-client/docs/dyn/fitness_v1.users.html 
            # でやる処理
            body =  {
            "aggregateBy": [
            {
                "dataTypeName": "com.google.sleep.segment"
            },
            ],
            "startTimeMillis": str(int(time.mktime(start_date.timetuple())) * 1000),
            "endTimeMillis": str(int(time.mktime(end_date.timetuple())) * 1000)
            }
            ret = self.authdata.users().dataset().aggregate(userId='me', body=body).execute()
        elif index=="sleep_session":
            # セッションアクティビティごとの処理
            # https://developers.google.com/fit/scenarios/read-sleep-data
            # の 1. Retrieve a list of sessions setting the activityType parameter to 72 (SLEEP). Note: You can use a startTime and endTime, or use a pageToken to retrieve new sessions since the previous request.
            # に則ったやりかたはこちら？
            starttime = start_date.isoformat("T") + "Z"
            endtime = end_date.isoformat("T") + "Z"
            ret = self.authdata.users().sessions().list(userId='me',activityType=72, fields='session',startTime=starttime,endTime=endtime).execute()
        elif index=="steps":
            # https://developers.google.com/fit/scenarios/read-daily-step-total
            # に則ったやりかた
            body =  {
            "aggregateBy": [{
                "dataTypeName": "com.google.step_count.delta",
                "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"            }],
            "bucketByTime": { "durationMillis": "86400000" },
            "startTimeMillis": str(int(time.mktime(start_date.timetuple())) * 1000),
            "endTimeMillis": str(int(time.mktime(end_date.timetuple())) * 1000)
            }
            ret = self.authdata.users().dataset().aggregate(userId='me', body=body).execute()
        else:
            ret = self.authdata.users().dataSources(). \
                datasets(). \
                get(userId='me', dataSourceId=self.DATA_SOURCE[index], datasetId=data_set). \
                execute()
        return ret

    def get_calorie(self):
        return self.cal_data

    def get_sleep(self):
        return self.sleep_data

    def get_sleep_session(self):
        return self.sleep_session_data

    def get_step(self):
        return self.steps_data