from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (SparkSession.builder
    .appName("bronze_to_silver_grades")
    .config("spark.jars.packages",
            "io.delta:delta-spark_2.12:3.2.0,"
            "org.apache.hadoop:hadoop-aws:3.3.4")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .getOrCreate())

spark.sparkContext.setLogLevel("WARN")

print("Reading raw grades from MinIO...")
raw = spark.read.parquet("s3a://unidata-raw/academic_performance/grades/")
print(f"Raw count: {raw.count()}")

silver = (raw
    .withColumn("grade", F.col("grade").cast("int"))
    .withColumn("graded_at", F.to_timestamp("graded_at"))
    .withColumn("event_date", F.to_date("graded_at"))
    .dropDuplicates(["grade_id"])
    .filter(F.col("grade").between(2, 5)))

print(f"Silver count: {silver.count()}")

(silver.write.format("delta")
    .mode("overwrite")
    .partitionBy("event_date")
    .save("s3a://unidata-silver/academic_performance/grades/"))

print("Done! Silver grades written to MinIO.")
spark.stop()
