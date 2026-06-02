from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64

student = Entity(name="student_id", join_keys=["student_id"])

src = FileSource(
    path="s3://unidata-gold/academic_performance/student_features/",
    timestamp_field="event_ts",
    s3_endpoint_override="http://localhost:9000",
)

student_features_v1 = FeatureView(
    name="student_features_v1",
    entities=[student],
    ttl=timedelta(days=2),
    schema=[
        Field(name="avg_grade_last_30d", dtype=Float32),
        Field(name="attendance_rate_30d", dtype=Float32),
        Field(name="grades_count_30d", dtype=Int64),
        Field(name="risk_score", dtype=Float32),
    ],
    source=src,
)
