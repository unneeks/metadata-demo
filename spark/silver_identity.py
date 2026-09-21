from pyspark.sql import SparkSession

def resolve_identity(spark):
    print("Resolving Identities...")
    try:
        # Just move the identity mapping to silver for now
        mapping = spark.read.csv("/opt/airflow/src/identity_mapping.csv", header=True)
        mapping.write.mode("overwrite").parquet("/opt/airflow/silver/identity_mapping")
    except Exception as e:
        print(f"Error resolving identity: {e}")
        
    print("Identity resolution complete.")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Silver Identity Resolution").getOrCreate()
    resolve_identity(spark)
    spark.stop()
