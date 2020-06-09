#from flask import Flask, render_template
import csv
import json
from pygeocoder import Geocoder
import googlemaps
import re
import os

#app= Flask(__name__)

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

columns = ["Image","Name1","Name2"]
df2 = pd.DataFrame(columns=columns)

for tr in real_page_tags:  # 繰り返しでtrタグの中のタグを取得
  tds = tr.find_all("td")
  # print(tds)
  for td in tds:
    Img = td.img
    Name1 = td.string
    Name2 = td.p
    se = pd.Series([Img,Name1,Name2],columns) #取得したImg,Name1,Name2をseに追加
    # print(se)
    df2 = df2.append(se, columns)#seをdf2に行で追加
    df3 = df2.reset_index().T.reset_index().T.values.tolist() 
# df2 #確認用
# df3 #確認用
dst = [] #空の配列を設定
for block in df3: #df3（配列)の１つ１つの値をfor文で繰り返し処理する宣言。(結果はblockに格納される)
    new_block = [x for x in block if x != None] #(blockの中にNoneがあれば取り除く)
    # ifの条件が成り立つもののみをリストに含める filter。「！=」等しくないの意
    #(参考：https://www.lifewithpython.com/2014/09/python-list-comprehension-and-generator-expression-and-dict-comprehension.html)
    dst.append(new_block) #空の配列にNoneを除いた配列を挿入
df3 = dst #df3にdstを代入
# print(df3) #確認用
columns_fix=["block","block2","block3","block4"]
df3_fix = pd.DataFrame(df3,columns=columns_fix) #block行列に変換！
# print(df3_fix)

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
    detail = requests.get(i["url"])
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
