import streamlit as st
import pandas as pd
import altair as alt
import requests

CH_URL = "http://localhost:8123"
CH_USER = "grafana"

def query_ch(sql):
    r = requests.post(CH_URL, params={"user": CH_USER}, data=sql)
    from io import StringIO
    return pd.read_csv(StringIO(r.text), sep="\t")

st.set_page_config(page_title="UniData", layout="wide")
st.title("Университетская платформа данных")

tab1, tab2 = st.tabs(["Кампус", "Успеваемость"])

with tab1:
    st.subheader("Загруженность аудиторий — последние 30 минут")

    df = query_ch("""
        SELECT room_id, sum(cnt) AS events
        FROM campus_events_5m
        WHERE event_time >= now() - INTERVAL 30 MINUTE
          AND event_type = 'entered_classroom'
        GROUP BY room_id
        ORDER BY events DESC
        LIMIT 20
        FORMAT TabSeparatedWithNames
    """)

    if not df.empty:
        chart = alt.Chart(df).mark_bar(color="#4CAF50").encode(
            x=alt.X("room_id:N", title="Аудитория", sort="-y"),
            y=alt.Y("events:Q", title="Входов"),
            tooltip=["room_id", "events"]
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Нет данных за последние 30 минут")

    st.subheader("Drill-down: активность по типу события")
    event_type = st.selectbox(
        "Выберите тип события:",
        ["entered_classroom", "left_classroom", "submitted_assignment"]
    )

    df2 = query_ch(f"""
        SELECT toStartOfMinute(event_time) AS t, sum(cnt) AS events
        FROM campus_events_5m
        WHERE event_type = '{event_type}'
          AND event_time >= now() - INTERVAL 1 HOUR
        GROUP BY t ORDER BY t
        FORMAT TabSeparatedWithNames
    """)

    if not df2.empty:
        df2["t"] = pd.to_datetime(df2["t"])
        line = alt.Chart(df2).mark_line(color="#2196F3").encode(
            x=alt.X("t:T", title="Время"),
            y=alt.Y("events:Q", title="Событий"),
            tooltip=["t", "events"]
        ).properties(height=300)
        st.altair_chart(line, use_container_width=True)

with tab2:
    st.subheader("Успеваемость студентов")
    st.info("Данные из Gold-слоя (Delta Lake) появятся после запуска Spark-трансформаций")

    col1, col2, col3 = st.columns(3)
    col1.metric("Студентов в системе", "500")
    col2.metric("Средний балл", "3.8")
    col3.metric("Посещаемость", "78%")
