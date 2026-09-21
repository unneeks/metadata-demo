from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

def standardize(spark):
    print("Standardizing schemas...")
    
    # Example: standardize Jira issues
    try:
        issues = spark.read.parquet("/opt/airflow/bronze/jira_issue")
        # Standardize timestamp formats, missing values, etc.
        silver_issues = issues.withColumn("created_date", to_timestamp(col("created_timestamp")))
        silver_issues.write.mode("overwrite").parquet("/opt/airflow/silver/work_item")
    except Exception as e:
        print(f"Error standardizing jira_issue: {e}")
        
    try:
        emp = spark.read.parquet("/opt/airflow/bronze/successfactors_employee")
        emp.write.mode("overwrite").parquet("/opt/airflow/silver/employee")
    except Exception as e:
        print(f"Error standardizing employee: {e}")
        
    print("Standardization complete.")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Silver Standardize").getOrCreate()
    standardize(spark)
    spark.stop()
