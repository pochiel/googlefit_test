from fitnessdata import fitnessdata
from datetime import datetime, timedelta

if __name__ == "__main__":
    fit = fitnessdata()

    # 前日分のデータを取得
    TODAY = datetime.today() - timedelta(days=1)
    start_day = TODAY - timedelta(days=23)
    STARTDAY = datetime(start_day.year, start_day.month, start_day.day, 0, 0, 0)            # 前日の 00:00:00
    NEXTDAY  = datetime(TODAY.year, TODAY.month, TODAY.day, 23, 59, 59)                     # 前日の 23:59:59
    fit.get_transaction(STARTDAY, NEXTDAY)

    cal_data = fit.get_calorie()
    #sleep_data = fit.get_sleep_session()
    sleep_data = fit.get_sleep()
    step_data = fit.get_step()

    # カロリーデータ
    #print("Cal data")
    #print("start_date , end_date , value")
    #for record in cal_data:
    #    print(datetime.fromtimestamp( record.start ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
    #        datetime.fromtimestamp( record.end ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
    #        str( record.value)
    #        )

    # 睡眠データ(ベッドの中にいる時間　深い眠りの時間などを取る方法がわからない)
    print("Sleep data")
    print("start_date , end_date , sleep_time")
    for record in sleep_data:
        print(datetime.fromtimestamp( record.start ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
            datetime.fromtimestamp( record.end ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
            str( (record.end - record.start) / 3600 ) + ',' +
            record.reason
            )

    # 歩数データ
    #print("Step count data")
    #print("start_date , end_date , Step_count")
    #for record in step_data:
    #    print(datetime.fromtimestamp( record.start ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
    #        datetime.fromtimestamp( record.end ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
    #        str( record.value)
    #        )
