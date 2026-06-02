from flask import Flask, jsonify
from datetime import datetime, timedelta, timezone
import random, uuid

app = Flask(__name__)
random.seed(42)

STUDENTS = [f"stu_{i:04d}" for i in range(500)]
COURSES = [f"crs_{i:02d}" for i in range(20)]


@app.route("/api/v1/grades")
def grades():
    out = []
    for _ in range(2000):
        out.append({
            "grade_id": str(uuid.uuid4()),
            "student_id": random.choice(STUDENTS),
            "course_id": random.choice(COURSES),
            "grade": random.choice([2, 3, 3, 4, 4, 4, 5, 5]),
            "graded_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))).isoformat(),
        })
    return jsonify(out)


@app.route("/api/v1/attendance")
def attendance():
    out = []
    for _ in range(5000):
        out.append({
            "student_id": random.choice(STUDENTS),
            "course_id": random.choice(COURSES),
            "session_dt": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))).isoformat(),
            "attended": random.random() > 0.2,
        })
    return jsonify(out)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
