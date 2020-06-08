from flask import Flask, render_template
import csv
import json
from pygeocoder import Geocoder
import googlemaps
import re
import os

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


# ここから物件個別の詳細情報をスクレイピングする処理

res_list = requests.get('https://www.city.saikai.nagasaki.jp/kurashi/jutaku/2/index.html')
soup_list = bs4(res_list.content,'lxml')
akiyaindex_data = soup_list.find_all('li', class_='page') # リンクの並んでいるpageをtagオブジェクトとして取得
url_list=[] #物件NoとURLのリストの枠を用意
for n in akiyaindex_data:
  url = n.a.get("href") #hrefのリンク先URLをget
  numbertext = n.text#tagオブジェクト内のテキスト情報を取得
  number = numbertext.strip("空き家情報(詳細)\n") #数字以外は削除
  if number.isdecimal(): #「空き家情報バンク」のトップページを抜いて、物件ナンバーに対するURLのみに絞る
    url_list.append({'number' : number, 'url' : url})
  else:
    pass
#print(url_list)

filename2 = "houselist.csv"
filepath = "./"+filename2
if os.path.exists(filepath):
    os.remove(filepath)

# URLごとの処理開始
for i in url_list:
  detail = requests.get(url)
  soup_detail = bs4(detail.content,'lxml')
  tdtags = soup_detail.find_all('td')
 # print(tdtags)
# imgの取得
  img1tagdiv = soup_detail.find(class_="image left-col")
  img2tagdiv = soup_detail.find(class_="image right-col")
 # あとで抽出しやすいように実データでない値のindexの頭には0をつけておく
  tabledata = pd.Series(tdtags, index=["0syozai", "address","0sintikunen","age","0torokuhi","date","0madori","floor","0torokukubun","category","0setubi" ,"facility","0kakaku","price","0tyusyajo","parking","0kouzou","architecture","0nuukyo","condition","0hutai","properties","0sonota","mention"], name=i['number'])
#  print(tabledata)
  tabledata = tabledata.sort_index() # スクレイピング結果のtdタグデータをソートする
  tabledata1 = tabledata[12:24] # 0がついたデータを抜いた
  dataframe = pd.DataFrame([tabledata1]) # 行から列に変換、tabledata1を行にしたデータフレームを作成

# 取得しておいたimgをデータフレームに追加
  img1tag = img1tagdiv.find("img")
  img1=img1tag["src"]
  img2tag = img2tagdiv.find("img")
  img2=img2tag["src"]

  dataframe["photo1"] = [img1]
  dataframe["photo2"] = [img2]

# 詳細用のCSVファイル出力
  dataframe.to_csv(filename2, mode='a',  header=False, index=True, encoding = 'utf-8-sig') 


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
        id_data = [[]]
        ids = []
        for row in datareader:
            n = datareader.line_num
            if(n > 4 and n % 6 == 4):
                name_data.append(row)
                a=row[2].strip('</p>\xa0')
                b=a.replace('\xa0（中戸）','')
                names.append(b) #csvで3つ目の列に住所が入っているという想定
            elif(n > 8 and n % 6 == 2):
                id_data.append(row)
                c=row[2].strip('</p>')
                ids.append(c)
#                print(ids)
            else:
                continue

# ここから緯度と経度を取る処理
        num = 0
        for locationname in names:
#                print(locationname)
                try:
                    geocode_result = gmaps.geocode(locationname)
                # loc
                    loc = locationname
                # lat
                    lat = geocode_result[0]['geometry']['location']['lat']
                # lng
                    lng = geocode_result[0]['geometry']['location']['lng']
                # id
                    id = ids[num]
                    loc_data.append({'id' : id, 'loc': loc, 'lat': lat, 'lng': lng})
                    num = num + 1
                except:
                    print('ERROR') # エラー処理はひとまずまとめておく

# ここから空き家詳細情報を取る処理
    #index.htmlに渡す配列
    house_list = {} 

    # houselist.csvから値をとる
    with open('houselist.csv', newline='', encoding='utf-8') as house_csv_data:
        housedatareader = csv.reader(house_csv_data, delimiter=',', lineterminator='\r\n')
        house_data = {}
        for row in housedatareader:
            house_id = row[0]

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
                'address':row[1].strip("</td><p>"),
                'age':row[2].strip("</td><p>"),
                'architecture':row[3].strip("</td><p>"),
                'category':row[4].strip("</td><p>"),
                'house_condition':row[5].strip("</td><p>"),
                'register_date':row[6].strip("</td><p>"),
                'facility':row[7].strip("</td><p>"),
                'floor':flr,
                'mention':row[9].strip("</td><p>"),
                'parking':row[10].strip("</td><p>"),
                'price':row[11].strip("</td><p>"),
                'ancillary_properties':row[12].strip("</td><p>"),
                'photo1':row[13],
                'photo2':row[14]
                }
            house_data.update({house_id:house_info})

#  index.htmlにモーダルウィンドウ表示用の空き家一覧情報を渡す
    return render_template("index6.html", GoogleMapApiKey=googlemapapikey , data=loc_data, house_detail=house_data)

if __name__ == "__main__":
    app.run(debug=True)

# ------表示時の実行処理ここまで--------------
