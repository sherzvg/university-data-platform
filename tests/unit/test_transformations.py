import pandas as pd


def filter_valid_grades(df):
    return df[df["grade"].between(2, 5)].drop_duplicates(subset=["grade_id"])


def test_filter_removes_invalid():
    df = pd.DataFrame([
        {"grade_id": "g1", "grade": 5},
        {"grade_id": "g2", "grade": 1},
        {"grade_id": "g3", "grade": 6},
    ])
    out = filter_valid_grades(df)
    assert len(out) == 1
    assert out["grade"].tolist() == [5]


def test_filter_keeps_valid_range():
    df = pd.DataFrame([
        {"grade_id": str(i), "grade": g}
        for i, g in enumerate([2, 3, 4, 5])
    ])
    out = filter_valid_grades(df)
    assert len(out) == 4


def test_dedup():
    df = pd.DataFrame([
        {"grade_id": "g1", "grade": 5},
        {"grade_id": "g1", "grade": 5},
        {"grade_id": "g2", "grade": 4},
    ])
    out = filter_valid_grades(df)
    assert len(out) == 2
