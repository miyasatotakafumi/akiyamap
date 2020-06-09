from flask import Flask, render_template
import csv
import json
from pygeocoder import Geocoder
import googlemaps
import re

app= Flask(__name__)
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
                print(ids)
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
                'address':row[1].strip("</td>").strip("\n<p>\n</p>").replace("</p>\n<p>",""),
                'age':row[2].strip("</td>\n</p>\n<p>"),
                'architecture':row[3].strip("</td>\n</p>\n<p>").replace("</p>\n<p>",""),
                'category':row[4].strip("</td>\n</p>\n<p>").replace("</p>\n<p>",""),
                'house_condition':row[5].strip("</td>\n</p>\n<p>").replace("</p>\n<p>","\n"),
                'register_date':row[6].strip("</td>\n</p>\n<p>"),
                'facility':row[7].strip("</td>\n</p>\n<p>").replace("</p>\n<p>",""),
                'floor':flr,
                'mention':row[9].strip("</td>\n</p>\n<p>").replace("</p>\n<p>",""),
                'parking':row[10].strip("</td>\n</p>\n<p>").replace("</p>\n<p>",""),
                'price':row[11].strip("</td>\n</p>\n<p>").replace("</p>\n<p>","\n"),
                'ancillary_properties':row[12].strip("</td>\n</p>\n<p>").replace("</p>\n<p>",""),
                'photo1':row[13],
                'photo2':row[14]
                }
            house_data.update({house_id:house_info})

#  index.htmlにモーダルウィンドウ表示用の空き家一覧情報を渡す
    return render_template("index.html", GoogleMapApiKey=googlemapapikey , data=loc_data, house_detail=house_data)

if __name__ == "__main__":
    app.run(debug=True)

# ------表示時の実行処理ここまで--------------
