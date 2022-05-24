from fitnessdata import fitnessdata
from lineIF import lineIF
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

def build_message(fit_data, message):
    ret = message
    # データ取得
    cal_data = fit_data.get_calorie()
    sleep_data = fit_data.get_sleep()
    step_data = fit_data.get_step()

    # カロリーデータ
    record = cal_data[1]
    ret = ret + "  ・消費カロリー：" + str( round( record.value, 2) ) + '\n'

    # 歩数データ
    record = step_data[1]
    ret = ret + "  ・歩数：" + str( round( record.value, 2) ) + '\n'
    ret = ret + '\n'

    # 睡眠データ
    ret = ret + "  ・睡眠データ\n"
    sleep_start = datetime(start_day.year, start_day.month, start_day.day, 17, 0, 0)
    sleep_end = datetime(TODAY.year, TODAY.month, TODAY.day, 16, 59, 59) 
    ret = ret + "    浅い睡眠:" + str( round( sum_reason(sleep_data, "light_sleep", sleep_start, sleep_end), 2) ) + "\n"
    ret = ret + "    深い睡眠:" + str( round( sum_reason(sleep_data, "deep_sleep", sleep_start, sleep_end), 2) ) + "\n"
    ret = ret + "    レム睡眠:" + str( round( sum_reason(sleep_data, "rem_sleep", sleep_start, sleep_end), 2) ) + "\n"
    ret = ret + "      その他:" + str( round( sum_reason(sleep_data, "sleep", sleep_start, sleep_end), 2) ) + "\n"

    return ret

if __name__ == "__main__":
    # フィットネスデータ管理クラス作成
    fit_me = fitnessdata("pochi")
    fit_papa = fitnessdata("papa")

    # LINEのインターフェースを作成
    line_if = lineIF()

    # 前日分のデータを取得
    TODAY = datetime.today() - timedelta(days=1)
    start_day = TODAY - timedelta(days=1)
    STARTDAY = datetime(start_day.year, start_day.month, start_day.day, 0, 0, 0)            # 前日の 00:00:00
    NEXTDAY  = datetime(TODAY.year, TODAY.month, TODAY.day, 23, 59, 59)                     # 前日の 23:59:59
    fit_me.get_transaction(STARTDAY, NEXTDAY)
    fit_papa.get_transaction(STARTDAY, NEXTDAY)

    message_me = "■" + NEXTDAY.strftime( '%Y-%m-%d') + "のワイ\n"
    message_papa = "■" + NEXTDAY.strftime( '%Y-%m-%d') + "のパッパ\n"

    message_me = build_message(fit_me, message_me)
    message_papa = build_message(fit_papa, message_papa)

    # 送信
    line_if.send_message(message_me)
    line_if.send_message(message_papa)
    print(message_me)
    print(message_papa)