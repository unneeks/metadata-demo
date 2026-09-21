import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, col
import os

def load_bronze(source, spark):
    print(f"Loading {source} to bronze...")
    base_path = f"/opt/airflow/src/{source}"
    
    if not os.path.exists(base_path):
        print(f"No source data found at {base_path}")
        return
        
    for file in os.listdir(base_path):
        if file.endswith(".csv"):
            table_name = file.replace(".csv", "")
            df = spark.read.csv(f"{base_path}/{file}", header=True, inferSchema=True)
            
            # Add Bronze metadata
            df = df.withColumn("ingestion_timestamp", current_timestamp()) \
                   .withColumn("source_system", lit(source)) \
                   .withColumn("source_file", lit(file)) \
                   .withColumn("batch_id", lit("BATCH_001"))
                   
            # In a real Iceberg environment:
            # df.writeTo(f"lakehouse.bronze.{source}_{table_name}").createOrReplace()
            # For local demo, we'll write to Parquet in the bronze/ folder
            out_path = f"/opt/airflow/bronze/{source}_{table_name}"
            df.write.mode("overwrite").parquet(out_path)
            print(f"Wrote {df.count()} records to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    args = parser.parse_args()
    
    spark = SparkSession.builder \
        .appName(f"Bronze Load - {args.source}") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.lakehouse.type", "hadoop") \
        .config("spark.sql.catalog.lakehouse.warehouse", "/opt/spark/warehouse") \
        .getOrCreate()
        
    load_bronze(args.source, spark)
    spark.stop()
