from flask import Flask, render_template

app= Flask(__name__)

# ----スクレイピング------------
import requests
from bs4 import BeautifulSoup as bs4

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

import pandas as pd
from google.colab import files
# データフレームを作成してください。列名は、name, urlです。
# columns = ["写真", "所在地","区分","売却価格/賃料","構造","詳細"]
columns = [img,name1,name2]
df2 = pd.DataFrame(columns=columns)
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
    print(se)
    df2 = df2.append(se, columns)
# result.csvという名前でCSVに出力してください。
filename = "result.csv"
df2.to_csv(filename, encoding = 'utf-8-sig') #encoding指定しないと、エラーが起こります。おまじないだともって入力します。
files.download(filename)

# ------スクレイピングここまで--------------

# ------表示時の実行処理ここから--------------
@app.route('/')

def main():
# result.csvから名前（住所）の値をとる
    with open('result.csv', newline='', encoding='utf-8') as csv_data:
        datareader = csv.reader(csv_data, delimiter=',', lineterminator='\r\n')
        print(csv_data)
        name_data = [["col1", "col2","col3","col4"]]
        names = []
        for row in datareader:
            n = datareader.line_num
            print(n)
            if(n % 6 == 3):
                name_data.append(row)
                names.append(row[3]) #csvで3つ目の列に住所が入っているという想定
            else:
                continue

# これはテスト用のreturn
        return render_template("index.html", data=names)

if __name__ == "__main__":
    app.run(debug=True)

# 次やること、緯度latと経度lonを取得
# GoogleMapAPIにKeyを渡す
# HTMLに名前と緯度経度を渡す　表示はrender_templateを使う
# GoogleMap初期地設定～表示まではHTML側で行う
# 検索Boxからの入力受け取り、値チェック

# ------表示時の実行処理ここまで--------------
