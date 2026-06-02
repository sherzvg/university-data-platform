import great_expectations as gx
import pandas as pd
import boto3
import io

# Подключиться к MinIO и скачать файл для валидации
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
)

# Найти последний файл grades
response = s3.list_objects_v2(Bucket="unidata-raw", Prefix="academic_performance/grades/")
files = [o["Key"] for o in response.get("Contents", []) if o["Key"].endswith(".parquet")]
if not files:
    print("No parquet files found!")
    exit(1)

latest = sorted(files)[-1]
print(f"Validating: {latest}")

obj = s3.get_object(Bucket="unidata-raw", Key=latest)
df = pd.read_parquet(io.BytesIO(obj["Body"].read()))
print(f"Shape: {df.shape}")
print(df.dtypes)

# Создать GE context и валидировать
context = gx.get_context()

ds = context.sources.add_or_update_pandas(name="grades_source")
da = ds.add_dataframe_asset(name="grades_asset")
batch_request = da.build_batch_request(dataframe=df)

suite = context.add_or_update_expectation_suite("raw_grades_suite")
validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite=suite,
)

# Ожидания
validator.expect_column_values_to_not_be_null("grade_id")
validator.expect_column_values_to_be_unique("grade_id")
validator.expect_column_values_to_be_in_set("grade", [2, 3, 4, 5])
validator.expect_table_row_count_to_be_between(min_value=100, max_value=100000)
validator.expect_column_values_to_not_be_null("student_id")
validator.expect_column_values_to_not_be_null("course_id")

validator.save_expectation_suite()

# Запустить валидацию
results = validator.validate()

print("\n=== Validation Results ===")
print(f"Success: {results.success}")
for r in results.results:
    status = "✅" if r.success else "❌"
    print(f"{status} {r.expectation_config.expectation_type}: {r.success}")

if not results.success:
    print("\nFailed expectations detected!")
    exit(1)
else:
    print("\nAll expectations passed!")
