from fitnessdata import fitnessdata
from datetime import datetime, timedelta

def sum_reason(data, reason, sleep_start, sleep_end):
    ret = 0.0
    for x in data:
        if (
            (x.reason == reason) and 
            (datetime.fromtimestamp(x.start) > sleep_start) and 
            (datetime.fromtimestamp(x.start) < sleep_end)
            ):
            ret = ret + (x.end - x.start) / 3600  
    return ret

if __name__ == "__main__":
    fit_me = fitnessdata("pochi")
    #fit_papa = fitnessdata("papa")

    # 前日分のデータを取得
    TODAY = datetime.today() - timedelta(days=1)
    start_day = TODAY - timedelta(days=1)
    STARTDAY = datetime(start_day.year, start_day.month, start_day.day, 0, 0, 0)            # 前日の 00:00:00
    NEXTDAY  = datetime(TODAY.year, TODAY.month, TODAY.day, 23, 59, 59)                     # 前日の 23:59:59
    fit_me.get_transaction(STARTDAY, NEXTDAY)
    #fit_papa.get_transaction(STARTDAY, NEXTDAY)

    # 自分のデータを取得
    cal_data = fit_me.get_calorie()
    #sleep_data = fit_me.get_sleep_session()
    sleep_data = fit_me.get_sleep()
    step_data = fit_me.get_step()

    # パッパのデータを取得
    #cal_data_papa = fit_papa.get_calorie()
    #sleep_data_papa = fit_papa.get_sleep()
    #step_data_papa = fit_papa.get_step()

    # カロリーデータ
    #print("Cal data")
    #print("start_date , end_date , value")
    #for record in cal_data:
    #    print(datetime.fromtimestamp( record.start ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
    #        datetime.fromtimestamp( record.end ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
    #        str( record.value)
    #        )

    # 睡眠データ
    print("Sleep data")
    print("start_date , end_date , sleep_time")
    sleep_start = datetime(start_day.year, start_day.month, start_day.day, 17, 0, 0)
    sleep_end = datetime(TODAY.year, TODAY.month, TODAY.day, 16, 59, 59) 
    print( "lite:" + str( sum_reason(sleep_data, "light_sleep", sleep_start, sleep_end) ))
    print( "deep:" + str( sum_reason(sleep_data, "deep_sleep", sleep_start, sleep_end) ))
    print( "rem:" + str( sum_reason(sleep_data, "rem_sleep", sleep_start, sleep_end) ))
    print( "sleep:" + str( sum_reason(sleep_data, "sleep", sleep_start, sleep_end) ))
    #for record in sleep_data:
    #    print(datetime.fromtimestamp( record.start ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
    #        datetime.fromtimestamp( record.end ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
    #        str( (record.end - record.start) / 3600 ) + ',' +
    #        record.reason
    #        )

    # 歩数データ
    #print("Step count data")
    #print("start_date , end_date , Step_count")
    #for record in step_data:
    #    print(datetime.fromtimestamp( record.start ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
    #        datetime.fromtimestamp( record.end ).strftime( '%Y-%m-%d %H:%M:%S') + ',' +
    #        str( record.value)
    #        )
