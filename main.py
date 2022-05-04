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

class fitnessdata:
    def __init__(self):
        self.authdata = self.auth_data()
        return

    def get_transaction_cal(self, start_date, end_date):
        ret = []
        START = int(time.mktime(start_date.timetuple())*1000000000)
        # カロリーデータ集計を取得
        self.cal_data_raw = self.retrieve_data(self.authdata, start_date, end_date, "cal")
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

    def get_transaction(self, start_date, end_date):
        print("start_date:" + str(start_date) + "    end_date:" + str(end_date))
        self.get_transaction_cal(start_date, end_date)
        self.sleep_data_raw = self.retrieve_data(self.authdata, start_date, end_date, "sleep")
        self.steps_data_raw = self.retrieve_data(self.authdata, start_date, end_date, "steps")

    OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read'
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

    def auth_data(self):
        credentials = ""
        if os.path.exists(self.CREDENTIALS_FILE):
            credentials = Storage(self.CREDENTIALS_FILE).get()
        else:
            flow = flow_from_clientsecrets(
                # API有効化時に取得したOAuth用のJSONファイルを指定
                './oauth2.json',
                # スコープを指定
                scope=self.OAUTH_SCOPE,
                # ユーザーの認証後の、トークン受け取り方法を指定（後述）
                redirect_uri=self.REDIRECT_URI)

            authorize_url = flow.step1_get_authorize_url()
            print('下記URLをブラウザで起動してください。')
            print(authorize_url)

            code = input('Codeを入力してください: ').strip()
            credentials = flow.step2_exchange(code)

            if not os.path.exists(self.CREDENTIALS_FILE):
                Storage(self.CREDENTIALS_FILE).put(credentials)

        # Create an httplib2.Http object and authorize it with our credentials
        http = httplib2.Http()
        http = credentials.authorize(http)

        fitness_service = build('fitness', 'v1', http=http)
        self.authdata = fitness_service
        return fitness_service


    def retrieve_data(self, fitness_service, start_date, end_date, index):
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
            ret = fitness_service.users().dataset().aggregate(userId='me', body=body).execute()
        else:
            ret = fitness_service.users().dataSources(). \
                datasets(). \
                get(userId='me', dataSourceId=self.DATA_SOURCE[index], datasetId=data_set). \
                execute()
        return ret

    def get_calorie(self):
        # print(self.cal_data.value)
        return self.cal_data

if __name__ == "__main__":
    fit = fitnessdata()

    # 前日分のデータを取得
    TODAY = datetime.today() - timedelta(days=1)
    start_day = TODAY - timedelta(days=23)
    STARTDAY = datetime(start_day.year, start_day.month, start_day.day, 0, 0, 0)            # 前日の 00:00:00
    NEXTDAY  = datetime(TODAY.year, TODAY.month, TODAY.day, 23, 59, 59)                     # 前日の 23:59:59
    fit.get_transaction(STARTDAY, NEXTDAY)

    cal_data = fit.get_calorie()
    print("start_date , end_date , value")
    for record in cal_data:
        print(datetime.fromtimestamp( record.start ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
            datetime.fromtimestamp( record.end ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
            str( record.value)
            )
