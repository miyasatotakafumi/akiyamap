from flask import Flask, render_template
import csv
import json
from pygeocoder import Geocoder
import googlemaps
import re

app= Flask(__name__)

# ----スクレイピング------------
import requests
from bs4 import BeautifulSoup as bs4
import pandas as pd
#from google.colab import files

#html_doc = requests.get("https://www.city.saikai.nagasaki.jp/kurashi/jutaku/2/2377.html").text
#soup = BeautifulSoup(html_doc, 'html.parser') # BeautifulSoupの初期化
res = requests.get('https://www.city.saikai.nagasaki.jp/kurashi/jutaku/2/2377.html')
soup = bs4(res.content,'lxml')
# print(soup.prettify())
real_page_tags = soup.find_all("tr") # 記事内の全てのtrタグを取得
for tr in real_page_tags:  # 繰り返しでtrタグの中のタグを取得
  tds = tr.find_all("td")
  for td in tds:
    # print(td.prettify())
    # print(td.string)
    # print(td.p)
    # print(td.img)

    # データフレームを作成してください。列名は、name, urlです。
    # columns = ["写真", "所在地","区分","売却価格/賃料","構造","詳細"]
    columns = ["img","name1","name2"]
    df2 = pd.DataFrame(columns=columns) #列名を指定している

# 記事名と記事URLをデータフレームに追加してください
for tr in real_page_tags:  # 繰り返しでtrタグの中のタグを取得
  tds = tr.find_all("td")
  for td in tds:
    # print(td.prettify())
    # print(td.string)
    # print(td.p)
    # print(td.img)
    img = td.img
    name1 = td.string
    name2 = td.p
    se = pd.Series([img,name1,name2], columns)
    # print(se)
    df2 = df2.append(se, columns)
    df3 = df2.reset_index().T.reset_index().T.values.tolist() #行・列を配列に変換
# print([x for x in df3 if x != None]) #df3の配列に存在する空要素""を除去
dst = [] #空の配列を設定
for block in df3: #df3の中のblock(配列）を繰り返し以下を読み取る
    new_block = [x for x in block if x != None] #blockの要素にNoneがあれば取り除く
    dst.append(new_block) #空の配列にNoneを除いた配列を挿入
df3 = dst #df3にdstを代入
print(df3)

columns_fix=["block","block2","block3","block4"]
df3_fix = pd.DataFrame(df3,columns=columns_fix) #列名を指定している
print(df3_fix)

# result.csvという名前でCSVに出力してください。
filename = "result.csv"
df3_fix.to_csv(filename, encoding = 'utf-8-sig') #encoding指定しないと、エラーが起こります。おまじないだともって入力します。
#files.download(filename)


# ------スクレイピングここまで--------------

# ------表示時の実行処理ここから--------------
@app.route("/")

def main():
    #API Keyを設定ファイルMapConfig.jsonから読み込み
    with open('MapConfig.json', newline='', encoding='utf-8') as mapkeys:
        keydata = json.load(mapkeys)
        googlemapapikey = keydata['JavaScriptKey']

    #Google Mapを用意
    gmaps = googlemaps.Client(key=googlemapapikey)
    #index.htmlに渡す配列
    loc_data = [] 

    # result.csvから名前（住所）の値をとる
    with open('result.csv', newline='', encoding='utf-8') as csv_data:
        datareader = csv.reader(csv_data, delimiter=',', lineterminator='\r\n')
        name_data = [[]]
        names = []
        for row in datareader:
            n = datareader.line_num
            if(n > 4 and n % 6 == 4):
                name_data.append(row)
                a=row[2].strip('</p>\xa0')
                b=a.replace('\xa0（中戸）','')
                names.append(b) #csvで3つ目の列に住所が入っているという想定
#                print(names)

            else:
                continue

# ここから緯度と経度を取る処理
        for locationname in names:
#                print(locationname)
                try:
                    geocode_result = gmaps.geocode(locationname)
#                   geocode_result = gmaps.geocode('大瀬戸町松島内郷352番地')
                # loc
                    loc = locationname
                # lat
                    lat = geocode_result[0]['geometry']['location']['lat']
                # lng
                    lng = geocode_result[0]['geometry']['location']['lng']
                    loc_data.append({'loc': loc, 'lat': lat, 'lng': lng})
                except:
                    print('ERROR') # エラー処理はひとまずまとめておく

# ここから空き家詳細情報を取る処理

    # houselist.csvから値をとる
    with open('houselist.csv', newline='', encoding='shift-jis') as house_csv_data:
        housedatareader = csv.reader(house_csv_data, delimiter=',', lineterminator='\r\n')
        house_data = {}
        for row in housedatareader:
            house_id = 'house'+row[0]

            # 間取りの箇所で、リンクがあればそのURLを抜き出す
            url_format = r'href=.*pdf'
            urltext = re.findall(url_format, row[8])
            #print(urltext)
            flrtext = ""
            for f in urltext:
                flrtext = flrtext + f

            if( urltext != []): # urltextに何か入っている　＝間取りがリンクになっていた場合
                flr = flrtext.replace('href=','') #リンクのURL中身を抜き出してflrに代入
            else: #間取りがリンクになっていない
                flr = row[8] # 元の値をそのまま入れておく

            house_info = {
                'id':row[0],
                'address':row[1],
                'register_date':row[2],
                'category':row[3],
                'price':row[4],
                'architecture':row[5],
                'ancillary_properties':row[6],
                'age':row[7],
                'floor':flr,
                'facility':row[9],
                'parking':row[10],
                'house_condition':row[11],
                'mention':row[12],
                'photo1':row[13],
                'photo2':row[14],
                'photo3':row[15],
                'appeal':row[16]
                }
            house_data.update({house_id:house_info})

#  index.htmlにAPIKeyと名前・緯度・経度のリスト、モーダルウィンドウ表示用の空き家一覧情報を渡す
    return render_template("index.html", GoogleMapApiKey=googlemapapikey , data=loc_data, house_detail=house_data)


if __name__ == "__main__":
    app.run(debug=True)

# 検索Boxからの入力受け取り、値チェック

# ページ更新
# ------表示時の実行処理ここまで--------------
