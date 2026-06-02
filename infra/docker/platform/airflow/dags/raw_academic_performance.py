from __future__ import annotations
import io, requests, pendulum
import pandas as pd
from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.exceptions import AirflowException

S3_CONN = "minio_s3"
RAW_BUCKET = "unidata-raw"
LMS_BASE = "http://lms-api:5001"


def telegram_alert(context):
    try:
        from airflow.providers.telegram.operators.telegram import TelegramOperator
        msg = (
            f"❌ DAG <b>{context['dag'].dag_id}</b>\n"
            f"Task: <code>{context['task_instance'].task_id}</code>\n"
            f"Time: {context['ts']}"
        )
        TelegramOperator(
            task_id="alert_failure",
            telegram_conn_id="telegram_default",
            text=msg,
        ).execute(context=context)
    except Exception as e:
        print(f"Telegram alert failed: {e}")


default_args = {
    "owner": "data-platform",
    "retries": 3,
    "retry_delay": pendulum.duration(minutes=1),
    "retry_exponential_backoff": True,
    "on_failure_callback": telegram_alert,
}


@dag(
    dag_id="raw_academic_performance",
    schedule="0 5 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Moscow"),
    catchup=False,
    default_args=default_args,
    tags=["raw", "academic_performance"],
)
def pipeline():

    @task
    def extract_grades(**context) -> str:
        ds = context["ds"]
        r = requests.get(f"{LMS_BASE}/api/v1/grades", timeout=30)
        r.raise_for_status()
        df = pd.DataFrame(r.json())
        if len(df) == 0:
            raise AirflowException("Empty grades response")
        key = f"academic_performance/grades/dt={ds}/grades.parquet"
        buf = io.BytesIO()
        df.to_parquet(buf, index=False)
        buf.seek(0)
        S3Hook(aws_conn_id=S3_CONN).load_bytes(
            buf.getvalue(), key=key, bucket_name=RAW_BUCKET, replace=True
        )
        return f"s3://{RAW_BUCKET}/{key}"

    @task
    def extract_attendance(**context) -> str:
        ds = context["ds"]
        r = requests.get(f"{LMS_BASE}/api/v1/attendance", timeout=30)
        r.raise_for_status()
        df = pd.DataFrame(r.json())
        key = f"academic_performance/attendance/dt={ds}/attendance.parquet"
        buf = io.BytesIO()
        df.to_parquet(buf, index=False)
        buf.seek(0)
        S3Hook(aws_conn_id=S3_CONN).load_bytes(
            buf.getvalue(), key=key, bucket_name=RAW_BUCKET, replace=True
        )
        return f"s3://{RAW_BUCKET}/{key}"

    @task
    def validate(grades_uri: str, attendance_uri: str):
        s3 = S3Hook(aws_conn_id=S3_CONN)
        for uri in [grades_uri, attendance_uri]:
            bucket, key = uri.replace("s3://", "").split("/", 1)
            obj = s3.get_key(key, bucket)
            if obj.content_length == 0:
                raise AirflowException(f"Empty file: {uri}")
        print(f"Validation OK: {grades_uri}, {attendance_uri}")

    g = extract_grades()
    a = extract_attendance()
    validate(g, a)


pipeline()
