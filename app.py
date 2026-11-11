import sqlite3
from pathlib import Path

from flask import Flask, abort, redirect, request, url_for

app = Flask(__name__)

DATABASE_PATH = Path(__file__).with_name("study_timer.db")



def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection




def initialize_database():
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS shelves(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            parent_id INTEGER ,
            FOREIGN KEY(parent_id) REFERENCES shelves(id)
            )
            """
        )
        connection.execute(
           """
            CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            time INTEGER NOT NULL DEFAULT 0,
            rate INTEGER NOT NULL DEFAULT 0,
            shelf_id INTEGER,
            FOREIGN KEY(shelf_id) REFERENCES shelves(id)
            )
           """
        )


initialize_database()


@app.route("/",methods = ['GET','POST'])
def home():

    with get_db_connection() as connection:
            if request.method == 'POST':
                name = request.form["name"]
                connection.execute(
                """
                INSERT INTO shelves(name) VALUES (?)
                """,(name,)
                )
                connection.commit()
                return redirect(url_for("home"))
            shelves = connection.execute("SELECT * FROM shelves WHERE parent_id IS NULL").fetchall()


    html = f"""
    <h1>ようこそ</h1>
    
    <form method = "POST">
    <p>本棚の名前：
        <input type = 'text' name = 'name'>
    </p>
    
    <button type = 'submit'>本棚を追加</button>
    </form>


    """

    for shelf in shelves:
        html += f"""
        <p>
            本棚：{shelf["name"]}
            <a href = "/shelves/{shelf['id']}">詳細</a>
        </p>
        """
    return html

@app.route("/shelves/<int:shelf_id>", methods=["GET","POST"])
def shelf_detail(shelf_id):
    with get_db_connection() as connection:
            if request.method =="POST":
                name = request.form['name']
                kind = request.form["kind"]
                if kind == "shelf":      
                    connection.execute(
                        """INSERT INTO shelves(name, parent_id) VALUES (?,?)
                    """,(name,shelf_id)
                    )
                
                elif kind == "book":
                    connection.execute(
                         """INSERT INTO books(name,shelf_id) VALUES(?,?)
                    """,(name,shelf_id)
                    )

                connection.commit()
                return redirect(url_for("shelf_detail", shelf_id = shelf_id))
                
        
            shelves = connection.execute(
                "SELECT * FROM shelves WHERE parent_id = ?",
                (shelf_id,)
            ).fetchall()

            books = connection.execute(
                 "SELECT * FROM books WHERE shelf_id = ?",
                 (shelf_id,)
            ).fetchall()

            shelf = connection.execute(
                "SELECT * FROM shelves WHERE id = ?",
                (shelf_id,)
            ).fetchone()


    html = f"""
    <h1>本棚：{shelf['name']}：の一覧</h1>
    <a href="{url_for('home')}">ホームに戻る</a>
    <form method="POST">
    <p>
    本棚の名前：
        <input type = "text" name = "name">
        </p>
        <button type = 'submit' name = "kind" value="shelf">本棚を追加</button>
    </form>        

    <form method="POST">
    <p>
    本の名前：
        <input type = "text" name = "name" >
        </p>
        <button type = "submit" name = "kind" value="book">本を追加</button>
    </form>
    """

    if shelf['parent_id'] is not None:
            html += f"""
            <a href="{url_for('shelf_detail', shelf_id = shelf['parent_id'])}">親本棚に戻る</a>
            """
        

    for shelf in shelves:
        html += f"""
        <p>
            本棚：{shelf["name"]}
            <a href = "/shelves/{shelf['id']}">詳細</a>
        </p>
        """
    for book in books:
         html += f"""
        <p>
            本：{book["name"]}
            <a href = "/books/{book['id']}">詳細</a>
        </p>
        """
    return html
                


            
@app.route("/books/<int:book_id>",methods=["GET"])
def book_detail(book_id):
    with get_db_connection() as connection:
         book = connection.execute("""
        SELECT * FROM books WHERE id = ?""",
        (book_id,)
         ).fetchone()

    html = f"""
    <h1>本：{book["name"]}の詳細</h1>
    <p>勉強時間：{book["time"]}分</p>
    <p>自己評価：{book["rate"]}/10</p>
    
    <a href="{url_for('shelf_detail', shelf_id = book['shelf_id'])}">親本棚に戻る</a>
    """
    return html




           
            
    
    html = f"""
    <h1>{subject['name']}</h1>
    <p>勉強時間：{subject['time']}時間</p>
    <p>自己評価：{subject['rate']}</p>
    
    <form method = "POST">
        <p>
            今回の勉強時間：
            <input type = 'number' name = 'time'>
        </p>

        <p>
            自己評価：
            <input type = 'number' name = 'rate'>
        </p>

        <button type = 'submit'>更新</button>
    </form>
    """

    return html


if __name__ == "__main__":
    app.run(debug=True)
