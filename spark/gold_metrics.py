from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, count, expr, lit, sum

def calculate_metrics(spark):
    print("Calculating metrics...")
    
    # In a real pipeline, we'd read from silver and write to gold.
    # For now, let's pretend to calculate Rework Rate from the issue history.
    try:
        history = spark.read.csv("/opt/airflow/src/jira/issue_history.csv", header=True)
        # simplistic rework calculation: count REOPENED statuses
        rework_calc = history.groupBy("issue_id").agg(
            sum(when(col("status") == "REOPENED", 1).otherwise(0)).alias("rework_count")
        )
        rework_calc = rework_calc.withColumn("rework_flag", when(col("rework_count") > 0, 1).otherwise(0))
        
        # Save intermediate metrics
        rework_calc.write.mode("overwrite").parquet("/opt/airflow/gold/metrics_rework")
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        
    print("Metrics calculated.")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Gold Metrics").getOrCreate()
    calculate_metrics(spark)
    spark.stop()
