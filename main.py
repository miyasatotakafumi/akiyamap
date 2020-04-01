from flask import Flask, render_template, redirect, secret_key

app= Flask(__name__)

@app.route('/')

def main():
// スクレイピング処理pyの呼び出し　-> 管理者が手動でやる、main.pyではしない
// 表示時には、すでにDBに値が入っている前提
// DBから名前と緯度と経度の値をとる

// GoogleMapAPIにKeyを渡す

// HTMLに名前と緯度経度を渡す　表示はrender_templateを使う


// GoogleMap初期地設定～表示まではHTML側で行う
// 検索Boxからの入力受け取り、値チェック

// ページ更新？

// 


