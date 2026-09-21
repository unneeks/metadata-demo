from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit

def create_delivery_product(spark):
    print("Creating Employee Delivery Data Product...")
    
    # We would join employee, team, rework metrics, cycle time, etc.
    # For this demonstrator, we will mock the final output structure.
    try:
        emp = spark.read.csv("/opt/airflow/src/successfactors/employee.csv", header=True)
        # Add mock metrics to simulate the Gold product
        gold = emp.withColumn("completed_work_items", lit(42)) \
                  .withColumn("median_cycle_time", lit(5.2)) \
                  .withColumn("rework_rate", lit(0.174)) \
                  .withColumn("change_related_incident_rate", lit(0.02)) \
                  .withColumn("review_participation", lit(0.85)) \
                  .withColumn("office_attendance_pattern", lit("HYBRID")) \
                  .withColumn("data_quality_score", lit(88)) \
                  .withColumn("data_quality_status", lit("PASS")) \
                  .withColumn("dq_status", lit("PASS"))
                  
        gold.write.mode("overwrite").parquet("/opt/airflow/gold/employee_delivery_data_product")
    except Exception as e:
        print(f"Error creating delivery product: {e}")
        
    print("Gold delivery product created.")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Gold Delivery Product").getOrCreate()
    create_delivery_product(spark)
    spark.stop()
