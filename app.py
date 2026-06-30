from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return """
<h1>ようこそ</h1>

<p>総勉強時間：0時間</p>

<hr>

<h2>基本情報</h2>
<p>勉強時間：0時間</p>
<p>自己評価：★★☆☆☆</p>

<a href="/basic">
    <button>詳細</button>
</a>

<hr>

<h2>数学A</h2>
<p>勉強時間：0時間</p>
<p>自己評価：★★★☆☆</p>

<a href="/mathA">
    <button>詳細</button>
</a>

"""
@app.route("/basic")
def basic():
    return"""
    <h1>基本情報</h1>

    <p>勉強時間：0時間</p>

    <button>開始</button>
    
    <a href="/">
        <button>ホームへ戻る</button>
    </a>
        
    """

@app.route("/mathA")
def mathA():
    return"""
    <h1>数学A</h1>
    
    <p>総勉強時間：0時間</p>
    
    <button>開始</button>
    
    <a href="/">
        <button>ホームへ戻る</button>
    </a>
    """

if __name__ == "__main__":
    app.run(debug=True)