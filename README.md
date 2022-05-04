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