import sqlite3
from pathlib import Path

from flask import Flask, abort, redirect, request, url_for

app = Flask(__name__)

DATABASE_PATH = Path(__file__).with_name("study_timer.db")
INITIAL_SUBJECTS = [
    ("basic", "基本情報", 0, 2),
    ("mathA", "数学A", 0, 3),
]


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

#dbリセットボタン。操作確認のため。
def reset_subjects(connection):
    connection.execute("DELETE FROM study_subjects")
    connection.executemany(
        "INSERT INTO study_subjects (id, name, time, rate) VALUES (?, ?, ?, ?)",
        INITIAL_SUBJECTS,
    )
    connection.commit()


def initialize_database():
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS study_subjects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                time INTEGER NOT NULL DEFAULT 0,
                rate INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        subject_count = connection.execute(
            "SELECT COUNT(*) FROM study_subjects"
        ).fetchone()[0]

        if subject_count == 0:
            connection.executemany(
                "INSERT INTO study_subjects (id, name, time, rate) VALUES (?, ?, ?, ?)",
                INITIAL_SUBJECTS,
            )
        connection.commit()


initialize_database()


@app.route("/")
def home():
    with get_db_connection() as connection:
        subjects = connection.execute("SELECT * FROM study_subjects ORDER BY id").fetchall()
        total = connection.execute("SELECT COALESCE(SUM(time), 0) FROM study_subjects").fetchone()[0]

    html = f"""
    <h1>ようこそ</h1>
    <p>総勉強時間：{total}時間</p>

    <form action="{url_for('reset')}" method="POST">
        <button type="submit">データをリセット</button>
    </form>
    """

    for subject in subjects:
        html += f"""
        <hr>
        <h2>{subject['name']}</h2>
        <p>勉強時間：{subject['time']}時間</p>
        <p>自己評価：{subject['rate']}</p>
        <a href="/{subject['id']}">
            <button>詳細</button>
        </a>
        """

    return html


@app.route("/reset", methods=["POST"])
def reset():
    with get_db_connection() as connection:
        reset_subjects(connection)
    return redirect(url_for("home"))


@app.route("/<subject_id>", methods=["GET", "POST"])
def subject_detail(subject_id):
    with get_db_connection() as connection:
        subject = connection.execute(
            "SELECT * FROM study_subjects WHERE id = ?",
            (subject_id,)
        ).fetchone()

        if request.method == "POST":
            added_time = int(request.form['time'])
            rate = int(request.form['rate'])

            connection.execute(
            """        
                UPDATE study_subjects
                SET time = time + ?,
                rate = ?
                WHERE id = ?
            """,
            (added_time, rate, subject_id)
            )

            connection.commit()

            subject = connection.execute(
            "SELECT * FROM study_subjects WHERE id = ?",
            (subject_id,)
        ).fetchone()

            
        

           
            
    
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
