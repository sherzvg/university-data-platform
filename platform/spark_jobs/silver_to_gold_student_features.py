from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("silver_to_gold").getOrCreate()
# ... та же конфигурация Spark + Delta ...

grades = spark.read.format("delta").load("s3a://unidata-silver/academic_performance/grades/")
attend = spark.read.format("delta").load("s3a://unidata-silver/academic_performance/attendance/")

w30 = F.col("graded_at") >= F.expr("current_timestamp() - INTERVAL 30 DAYS")

g = (grades.filter(w30)
        .groupBy("student_id")
        .agg(F.avg("grade").alias("avg_grade_last_30d"),
             F.count("*").alias("grades_count_30d")))

a = (attend.filter(F.col("session_dt") >= F.expr("current_timestamp() - INTERVAL 30 DAYS"))
        .groupBy("student_id")
        .agg(F.avg(F.col("attended").cast("int")).alias("attendance_rate_30d")))

features = (g.join(a, "student_id", "outer")
              .withColumn("risk_score",
                  F.when(F.col("avg_grade_last_30d") < 3.0, 0.8)
                   .when(F.col("attendance_rate_30d") < 0.6, 0.6)
                   .otherwise(0.2))
              .withColumn("event_ts", F.current_timestamp()))

(features.write.format("delta")
    .mode("overwrite")
    .save("s3a://unidata-gold/academic_performance/student_features/"))

spark.stop()