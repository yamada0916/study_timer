import sqlite3
from pathlib import Path

from flask import Flask, abort, redirect, request, url_for

app = Flask(__name__)

DATABASE_PATH = Path(__file__).with_name("study_timer.db")
INITIAL_SUBJECTS = [
    ("basic", "基本情報", 0, "★★☆☆☆"),
    ("mathA", "数学A", 0, "★★★☆☆"),
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
                rate TEXT NOT NULL
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
            "SELECT * FROM study_subjects WHERE id = ?", (subject_id,)
        ).fetchone()

        if subject is None:
            abort(404)

        if request.method == "POST":
            time_text = request.form.get("time", "").strip()
            rate_text = request.form.get("rate", "").strip()

            added_time = int(time_text) if time_text.isdigit() else 0
            current_rate = subject["rate"]

            if rate_text.isdigit() and 1 <= int(rate_text) <= 5:
                selected_rate = int(rate_text)
                current_rate = "★" * selected_rate + "☆" * (5 - selected_rate)

            connection.execute(
                "UPDATE study_subjects SET time = time + ?, rate = ? WHERE id = ?",
                (added_time, current_rate, subject_id),
            )
            connection.commit()
            subject = connection.execute(
                "SELECT * FROM study_subjects WHERE id = ?", (subject_id,)
            ).fetchone()

    current_rate = subject["rate"].count("★")
    html = f"""
    <h1>{subject['name']}</h1>
    <p>勉強時間：{subject['time']}時間</p>
    <p>自己評価：{subject['rate']}</p>

    <form method="POST">
        <p>
            今回の勉強時間：<input type="number" name="time" min="0" required>
        </p>
        <p>
            全体の自己評価：
            <span id="stars">
                <button type="button" class="star" data-rate="1">☆</button>
                <button type="button" class="star" data-rate="2">☆</button>
                <button type="button" class="star" data-rate="3">☆</button>
                <button type="button" class="star" data-rate="4">☆</button>
                <button type="button" class="star" data-rate="5">☆</button>
            </span>
            <input type="hidden" name="rate" id="rate" value="{current_rate}" required>
        </p>
        <button type="submit">更新</button>
    </form>

    <a href="/">
        <button>ホームへ戻る</button>
    </a>

    <script>
        const stars = document.querySelectorAll(".star");
        const rateInput = document.getElementById("rate");

        function showStars(selectedRate) {{
            stars.forEach((star) => {{
                const starRate = Number(star.dataset.rate);
                star.textContent = starRate <= selectedRate ? "★" : "☆";
            }});
        }}

        stars.forEach((star) => {{
            star.addEventListener("click", () => {{
                const selectedRate = Number(star.dataset.rate);
                rateInput.value = selectedRate;
                showStars(selectedRate);
            }});
        }});

        showStars(Number(rateInput.value));
    </script>
    """

    return html


if __name__ == "__main__":
    app.run(debug=True)
