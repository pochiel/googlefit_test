# googlefit を使うために悪戦苦闘した記録

まずはこの辺を参考に。

https://qiita.com/kusunamisuna/items/669fa324d4612dfdd7bf

https://developers.google.com/fit/rest/v1/get-started


# 集約されたデータ取得
https://developers.google.com/fit/rest/v1/data-sources
URI：https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate

# POST request の作り方
https://cloud.google.com/ai-platform/training/docs/python-client-library?hl=ja

    response = ml.projects().models().create(parent=project_id,
                                            body=request_dict).execute()

serviceごとに、リクエスト生成のための関数があるっぽいが、それの使い方がワカンネ
　→https://googleapis.github.io/google-api-python-client/docs/dyn/fitness_v1.html

# ■プロジェクト番号の使い方
https://for-dummies.net/gas-noobs/how-to-deploy-as-an-excutable-api-by-gas/
https://console.cloud.google.com/home/dashboard

# ■build の使い方への誘導
https://stackoverflow.com/questions/64923395/how-do-i-resolve-the-attributeerror-resource-object-has-no-attribute-in-googl

この、startTimeMillis と endTimeMillis がうまく設定できて、POST できれば
いい感じに行けそうな気がする。
　→main.py 参考に

# ■steps の集計
https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate
にPOSTリクエスト。
リクエストボディは下記
    {
    "aggregateBy": [{
        "dataTypeName": "com.google.step_count.delta",
        "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
    }],
    "bucketByTime": { "durationMillis": 86400000 },
    "startTimeMillis": 1650639600000,
    "endTimeMillis": 1650725880000
    }

# ■sleep データの取得
https://developers.google.com/fit/scenarios/read-sleep-data

最初うまく行かなかったが下記が違ったみたい
・OAUTH_SCOPE に 'https://www.googleapis.com/auth/fitness.sleep.read'が含まれていなかった
・https://www.googleapis.com/fitness/v1/users/userId/dataset:aggregate の userId は me に変える
・POST時に bucketByTime を指定しない

GETで取る方法は下記
https://github.com/cyberjunky/home-assistant-google_fit/blob/3269f709a9792fa36d67e0228a5e7506bb28feb6/custom_components/google_fit/sensor.py#L597
でもどうやらこれで取得できるのは「寝床にいた時間」みたいで「実際に寝ていた時間」を計算することができない・・・

# datasource の取得方法
GET https://www.googleapis.com/fitness/v1/users/me/dataSources

# google cloud API playground の使い方
https://developers.google.com/oauthplayground/
* OAuthプレイグラウンドに移動します。
* [ステップ1]で[APIを選択して承認] 、[Fitness v1]を展開し、使用するFitnessスコープを選択します。
* Step1 で Authrize API のボタンを押すと、いつもの google 認証画面が出るので認証しましょう
* Exchange authorization うんちゃらボタンを押す
* 

# Line Bot としてメッセージを送りたい
https://qiita.com/kro/items/67f7510b36945eb9689b

https://first-contact.jp/blog/article/linebot/

https://keinumata.hatenablog.com/entry/2018/05/08/122348

この辺のプログラムは bot宛のメッセージを受信したとき LINE 側が WebHook してくれるのをキャッチして
ハンドラを立ち上げ、応答するような使い方を想定している。（普通はそうだよね）
だけど、このシステムは定期的に動いて一方的にメッセージを送りつけるだけなのでそんなのいらないはずだ。
Herokuとか使わなくても、ラズパイで十分動かせるはず。

# Herokuに登録
Heroku scheduler を使うんじゃ
https://hashikake.com/heroku-scheculer
